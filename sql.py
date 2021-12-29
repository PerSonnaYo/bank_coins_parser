import mysql.connector as myc
from mysql.connector import Error
import pandas as pd

def create_server_connection(host_name, user_name, user_passowrd):
    connection = None
    try:
        connection = myc.connect(
            host = host_name,
            user = user_name,
            password = user_passowrd
        )
        print("MySQL Server connection successful")
    except Error as err:
        print(f"Error: '{err}'")
    return connection

def create_database(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        print("Database created successfully")
    except Error as err:
        print(f"Error: '{err}'")

def create_db_connection(host_name, user_name, user_passowrd, db_name):
    connection = None
    try:
        connection = myc.connect(
            host=host_name,
            user=user_name,
            password=user_passowrd,
            database = db_name
        )
        print("MySQL Database connection successful")
    except Error as err:
        print(f"Error: '{err}'")
    return connection

def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Query successful")
    except Error as err:
        print(f"Error: '{err}'")

def execute_query_for_val(connection, block):
    cursor = connection.cursor()
    try:
        cursor.execute("""
    insert into avito_base(name, price, date, link) values(%(name)s, %(price)s, %(date)s, %(link)s)""",
    {
        'name':block.title,
        'price':block.price,
        'date':block.date,
        'link':block.url
    })
        connection.commit()
        print("Query successful")
    except Error as err:
        print(f"Error: '{err}'")

def execute_alter(connection, pp):
    cursor = connection.cursor()
    try:
        cursor.execute(pp)
        connection.commit()
        print("Query successful")
    except Error as err:
        print(f"Error: '{err}'")

def create_table(coins_table):
    connection = create_db_connection('localhost', 'root', '4665335', 'test')
    execute_query(connection, coins_table)
    return connection