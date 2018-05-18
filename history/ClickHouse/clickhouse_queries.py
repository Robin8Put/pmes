"""
Custom module for SQL queries
"""
import datetime
import re

# Simple ClickHouse driver for queries
from clickhouse_driver import Client

# ClickHouse ORM for handling with databases
from infi.clickhouse_orm.database import Database


# Create database if it doesn't exist
db = Database('HistoryDB')

# Create client instance
client = Client('localhost', database='HistoryDB')


def find_transaction_number():
    """
    Find needed transaction number for checking integrity
    :return: id of transaction table
    """

    tables = client.execute("SHOW TABLES")

    tables_list = [i[0] for i in tables]

    tx_indexes = [tables_list[i] for i, item in enumerate(tables_list) if re.search(r"\btxhist\w*?\d+\b", item)]

    tx_idx = [re.findall('\d+', i)[0] for i in tx_indexes]

    try:
        return max(tx_idx)
    except ValueError:
        return None


def create_table(table, data):
    """
    Create table with defined name and fields
    :return: None
    """

    fields = data['fields']
    query = '('
    indexed_fields = ''

    for key, value in fields.items():
        non_case_field = value[0][0:value[0].find('(')]

        if non_case_field == 'int':
            sign = value[0][value[0].find(',') + 1:-1:].strip()
            if sign == 'signed':
                field_type = 'Int'
            else:
                field_type = 'UInt'

            bits = re.findall('\d+', value[0])[0]
            field = key + ' ' + field_type + bits
            query += field + ','

        elif non_case_field == 'strin':
            field_type = 'String'
            field = key + ' ' + field_type
            query += field + ','

        elif non_case_field == 'float':
            field_type = 'Float'
            bits = re.findall('\d+', value[0])[0]
            field = key + ' ' + field_type + bits
            query += field + ','

        if value[1] == 'yes':
            indexed_fields += key + ','

    query = query[:-1:] + f",date Date) ENGINE = MergeTree(date, ({indexed_fields} date), 8192)"

    client.execute(f"CREATE TABLE {table} {query}")


def insert_into_table(table, data):
    """
    SQL query for inserting data into table
    :return: None
    """

    fields = data['fields']
    fields['date'] = datetime.datetime.now().date()

    query = '('

    for key in fields.keys():
        query += key + ','

    query = query[:-1:] + ")"

    client.execute(f"INSERT INTO {table} {query} VALUES", [tuple(fields.values())])


def select_from_table(fields, table, query):
    """
    SQL query for selecting data from certain table
    :return: selected data
    """

    select_data = client.execute(f"SELECT {fields} FROM {table} {query}", with_column_types=True)

    keys = [i[0] for i in select_data[1]]

    result = []

    for i in range(len(select_data[0])):
        result.append(dict(list(zip(keys, select_data[0][i]))))

    return result


def drop_table(table):
    """
    SQL query for dropping table
    :return: None
    """

    client.execute(f"DROP TABLE IF EXISTS {table}")
