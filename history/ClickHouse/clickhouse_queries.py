"""
Custom module for SQL queries
"""
import datetime

# Simple ClichHouse driver for queries
from clickhouse_driver import Client

# ClickHouse ORM for handling with databases
from infi.clickhouse_orm.database import Database


# Create database if it doesn't exist
db = Database('HistoryDB')

# Create client instance
client = Client('localhost', database='HistoryDB')


def create_table(name):
    """
    SQL query for creating table with defined name
    :return None
    """

    client.execute(f"CREATE TABLE IF NOT EXISTS {name} (id Int32, "
                   f"module String,"
                   f"event String,"
                   f"date Date,"
                   f"datetime DateTime,"
                   f"args Array(String)) ENGINE = MergeTree(date, (id, date), 8192)")


def insert_into_table(table, module, event, args):
    """
    SQL query for inserting data into certain table
    :return id of created instance
    """

    last_id = client.execute(f"SELECT MAX(id) FROM {table}")
    next_id = last_id[0][0]+1

    client.execute(f"INSERT INTO {table} (id, module, event, date, datetime, args) VALUES",
                   [(next_id, module, event, datetime.datetime.now().date(), datetime.datetime.now(), args)])

    return next_id


def select_from_table(table, query):
    """
    SQL query for selecting data from certain table
    :return: selected data
    """

    select_data = client.execute(f"SELECT * FROM {table} {query}")

    return select_data


def drop_table(table):
    """
    SQL query for dropping table
    :return: None
    """

    client.execute(f"DROP TABLE IF EXISTS {table}")
