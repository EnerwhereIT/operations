# This scripts imports daily the meter readings for revenue meters
# on active plants.
# Date: 6 August 2020
# User: Frank Wacker
# change log here

from __future__ import unicode_literals

import datetime
import json
import requests
import frappe,erpnext,operations
from frappe import database

def execute():
    # 1st get all plants
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    plants = getPlants()

    # 2nd get Data from Management DB

    for plant in plants:
        readings = getReading(yesterday)
        newRead = frappe.get_doc({
            'doctype': 'Meter Reading',
            'title': 'New Meter Reading'})
        newRead.name = yesterday.strftime() + readings.serial_no
        newRead.serial_no = readings.serial_no
        newRead.plant = readings.plant
        newRead.reading_date = readings.date
        newRead.value = readings.value
        newRead.insert()


def getReading(date):
    url = 'https://api.enerdata.com.........'
    headers = {
    'Authorization': 'Bearer ' +access_token,
    'Content - Type': 'application / json; charset = utf - 8'
    }
    r = requests.get(url, headers=headers)
    rs = r.json()
    return rs

def getPlants(today):
    plants = frappe.db.get_list('Plants',
                                filters={
                                    'type': 'Off-Grid',
                                    'plant_from': ['<',today],
                                    'plant_to':['=', '2999-12-31']
                                },
                                fields=['extid']
                                )
    return plants