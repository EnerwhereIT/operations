

from __future__ import unicode_literals
import datetime
import json
import requests
import frappe,erpnext,operations
from frappe import database

import mysql.connector
from mysql.connector import Error

try:
    connection = mysql.connector.connect(host='localhost',
                                         database='_90a8834de7632686',
                                         user='root',
                                         password='D4Emlmc!')
    cursor = connection.cursor()
    print("Displaying record Before Deleting it")
    sql_select_query = """SELECT *, left(name,14) as name1 FROM `_90a8834de7632686`.`tabPurchase Invoice` """
    cursor.execute(sql_select_query)
    records = cursor.fetchall()
    print(records)
    temp = ' '

    for record in records:
        if record.name1 == temp:
            sql_Delete_query = """Delete from tabPurchase Invoice where name = record.name"""
            cursor.execute(sql_Delete_query)
            connection.commit()

        temp = record.name1


except mysql.connector.Error as error:
    print("Failed to delete record from table: {}".format(error))
finally:
    if (connection.is_connected()):
        cursor.close()
        connection.close()
        print("MySQL connection is closed")


