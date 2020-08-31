# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import calendar
import datetime
import requests
import json

class PostJVs(Document):
	pass


@frappe.whitelist()
def post_jvs():
	mon = {
		"Jan": 1,
		"Feb": 2,
		"Mar": 3,
		"Apr": 4,
		"May": 5,
		"Jun": 6,
		"Jul": 7,
		"Aug": 8,
		"Sep": 9,
		"Oct": 10,
		"Nov": 11,
		"Dec": 12
	}

	me = frappe.get_doc("Post JVs")
	start_date = datetime.date(int(me.year),mon.get(me.month),1)
	# print(start_date)
	end_date = datetime.date(int(me.year),mon.get(me.month),calendar.monthrange(int(me.year), mon.get(me.month))[1])
	# print(end_date)
	period = me.month+"-"+me.year
	check = frappe.db.get_value("Journal Entry", {"period": period, "docstatus": 1},"name")
	if check:
		if me.override:
			doc = frappe.get_doc("Journal Entry", check)
			doc.cancel()
			frappe.delete_doc("Journal Entry", check)
			count = check_n_create(start_date, end_date, period)
			return count
		else:
			frappe.throw("Journal Entry also found for period {}-{}, Ref No# {}".format(me.month,me.year,check))
	else:
		count = check_n_create(start_date, end_date, period)
		return count
		

def check_n_create(start_date, end_date, period):
	count = 0
	url = "https://api.enerwhere-data.com/management/profitability/?accesskey=4E9135480112470734D98AF67FBA6B7E"
	x = requests.get(url)
	result = json.loads(x.text)
	invoices_total = frappe.db.sql("""select p.project,SUM(p.total) from `tabPurchase Invoice` p
		where p.docstatus=1 and p.is_deisel_invoice=1 and p.posting_date between %s and %s
		group by project""",(start_date, end_date))
	if invoices_total:
		for d in invoices_total:
			plant = get_plant_name(d[0])
			if plant:
				consumption = 0
				for i in result:
					if i.get("plant_name") == plant:
						date = i.get("Date_Time").split("T")[0]
						date = frappe.utils.getdate(date)
						print(date)
						# print(end_date)
						if date >= start_date and date <= end_date:
							consumption += i.get("Fuel_Consumption_Cost") or 0.0
							print(consumption)
				if consumption:
					create_jv(end_date, consumption, period, d[0])
					count+=1
	return count

def create_jv(end_date, consumption, period, project):
	doc = frappe.new_doc("Journal Entry")
	doc.posting_date = end_date
	doc.period = period
	doc.company = "Enerwhere Sustainable Energy DMCC"
	doc.append("accounts", {
			"account": "Direct Purchase - DMCC",
			"debit_in_account_currency": consumption,
			"project": project
		})
	doc.append("accounts", {
			"account": "Direct Purchase (inventory) - DMCC",
			"credit_in_account_currency": consumption,
			"project": project
		})
	doc.insert()
	doc.submit()

def create_invoice():
	doc = frappe.new_doc("Purchase Invoice")
	doc.supplier = "ABDEL WAHAB"
	doc.company = "Enerwhere Sustainable Energy DMCC"
	doc.project = "Camp Abu Dhabi"
	doc.is_deisel_invoice=1
	doc.append("items", {"item_code": "CS3U-375MB-AG", "qty": 1, "rate": 10, "project": "Camp Abu Dhabi"})
	doc.insert()
	doc.submit()

def get_plant_name(project):
	plant = frappe.db.sql("select parent from `tabPlant Project` where site_project_code = %s and project_decommissioning_date IS NULL",(project))
	if plant: return plant[0][0]
		# plant_id = frappe.db.get_value("Plants", plant[0][0], "plant_id")
		# if plant_id: return plant_id

def test():
	url = "https://api.enerwhere-data.com/management/profitability/?accesskey=4E9135480112470734D98AF67FBA6B7E"
	x = requests.get(url)
	result = json.loads(x.text)
	print(result)