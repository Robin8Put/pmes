import tornado.web
import clickhouse_queries

from jsonrpcserver.aio import methods
from jsonrpcclient.http_client import HTTPClient

from clickhouse_driver.errors import ServerException
from requests.exceptions import ConnectionError


@methods.add
async def create_table(**data):
    """
    RPC method for logging events and writing data to the database
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
async def refill_inc(**data):
    """
    RPC method for refilling user balance and sending this to the balance server
    :return: None
    """

    balance_host = "http://192.168.1.92:9888"
    client = HTTPClient(balance_host)

    table = 'Refill'
    data['fields'] = {'uid': data['uid'], 'coinid': data['coinid'], 'amount': data['value']}

    try:
        clickhouse_queries.insert_into_table(table, data)
        client.request(method_name="incbalance", uid=data["uid"], coinid=data["coinid"], amount=data["value"])
        return 'Data was successfully inserted into table'

    except ServerException as e:
        exception_code = int(str(e)[5:8].strip())

        if exception_code == 60:
            return 'Table does not exists'
        elif exception_code == 50:
            return 'Invalid params'

    except ConnectionError:
        return 'Balance server is not available'


@methods.add
async def refill_dec(**data):
    """
    RPC method for refilling user balance and sending this to the balance server
    :return: None
    """

    balance_host = "http://192.168.1.92:9888"
    client = HTTPClient(balance_host)

    table = 'Refill'
    data['fields'] = {'uid': data['uid'], 'coinid': data['coinid'], 'amount': data['value']}

    try:
        clickhouse_queries.insert_into_table(table, data)
        client.request(method_name="decbalance", uid=data["uid"], coinid=data["coinid"], amount=data["value"])
        return 'Data was successfully inserted into table'

    except ServerException as e:
        exception_code = int(str(e)[5:8].strip())

        if exception_code == 60:
            return 'Table does not exists'
        elif exception_code == 50:
            return 'Invalid params'

    except ConnectionError:
        return 'Balance server is not available'


@methods.add
async def refill_from_history(**data):
    """
    RPC method for refilling balance from history database and sending it to balance server
    :return: user balance
    """

    coin_id = data.get('coinid')
    user_id = data.get('uid')

    select_data = clickhouse_queries.select_from_table(table='Refill',
                                                       query=f"WHERE uid={user_id} AND coinid='{coin_id}'",
                                                       fields="amount")

    balance = 0

    for row in select_data:
        balance += row[0]

    return str(balance)


@methods.add
async def integrity(**data):
    """
    Method for checking lack of integrity in tables by order id
    :return: True or False
    """

    order_id = data.get("order_id")
    table = data.get("table")

    try:
        select_data = clickhouse_queries.select_from_table(table=table,
                                                           query=f"WHERE order_id={order_id}",
                                                           fields="order_id, status")

    except ServerException as e:
        exception_code = int(str(e)[5:8].strip())

        if exception_code == 60:
            return 'Table does not exist'
        elif exception_code == 50:
            return 'Invalid params'

    count_of_start_trasnaction = select_data.count((order_id, "start"))
    count_of_end_transaction = select_data.count((order_id, "end"))

    if count_of_start_trasnaction == count_of_end_transaction:
        return True

    else:
        return False


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
            return 'Table does not exist'
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
            return 'Table does not exist'


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