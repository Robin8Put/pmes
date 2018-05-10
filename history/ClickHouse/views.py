import tornado.web
import clickhouse_queries

from jsonrpcserver.aio import methods


@methods.add
async def log(**data):
    """
    RPC method for logging events and writing data to the database
    :return event id
    """

    table = data['table']

    clickhouse_queries.create_table(table)

    event_id = clickhouse_queries.insert_into_table(table=table,
                                                    module=data['module'],
                                                    event=data['event'],
                                                    args=data['args'])

    return str(event_id)


@methods.add
async def select(**data):
    """
    RPC method for selecting data from the database
    :return selected data
    """

    select_data = clickhouse_queries.select_from_table(table=data['table'], query=data['query'])

    return str(select_data)


@methods.add
async def drop(**data):
    """
    RPC method for deleting table from the database
    :return None
    """

    table = data['table']

    clickhouse_queries.drop_table(table)


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
