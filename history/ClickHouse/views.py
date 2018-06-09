import json
import tornado.web
import clickhouse_queries

from jsonrpcserver.aio import methods
from jsonrpcclient.http_client import HTTPClient

from clickhouse_driver.errors import ServerException
from requests.exceptions import ConnectionError


@methods.add
async def create_table(**data):
    """
    RPC method for creating table with custom name and fields
    :return event id
    """

    table = data.get('table')

    try:
        clickhouse_queries.create_table(table, data)
        return 'Table was successfully created'

    except ServerException as e:
        exception_code = int(str(e)[5:8].strip())

        if exception_code == 57:
            return 'Table already exists'
        elif exception_code == 50:
            return 'Invalid params'


@methods.add
async def insert(**data):
    """
    RPC method for inserting data to the table
    :return: None
    """

    table = data.get('table')

    try:
        clickhouse_queries.insert_into_table(table, data)
        return 'Data was successfully inserted into table'

    except ServerException as e:
        exception_code = int(str(e)[5:8].strip())

        if exception_code == 60:
            return 'Table does not exists'
        elif exception_code == 50:
            return 'Invalid params'


@methods.add
async def select(**data):
    """
    RPC method for selecting data from the database
    :return selected data
    """

    try:
        select_data = clickhouse_queries.select_from_table(table=data['table'], query=data['query'], fields=data['fields'])
        return str(select_data)

    except ServerException as e:
        exception_code = int(str(e)[5:8].strip())

        if exception_code == 60:
            return 'Table does not exists'
        elif exception_code == 50:
            return 'Invalid params'


@methods.add
async def drop(**data):
    """
    RPC method for deleting table from the database
    :return None
    """

    table = data['table']

    try:
        clickhouse_queries.drop_table(table)
        return 'Table was successfully deleted'

    except ServerException as e:
        exception_code = int(str(e)[5:8].strip())
        if exception_code == 60:
            return 'Table does not exists'


class HistoryHandler(tornado.web.RequestHandler):
    """
    Handler of RPC requests
    Accepts json-rpc data
    """

    async def post(self):
        """
        Accepts json-rpc post request.
        Retrieves data from request body.
        Calls defined method in field 'method_name'
        """

        request = self.request.body.decode()
        response = await methods.dispatch(request)
        if not response.is_notification:
            self.write(response)
