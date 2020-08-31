# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt
from operations.operations.report.financial_statements import (get_period_list, get_columns, get_data)

def execute(filters=None):
	period_list = get_period_list(filters.from_fiscal_year, filters.to_fiscal_year,
		filters.periodicity, filters.accumulated_values, filters.company)

	sales_account = frappe.db.get_value("Account", {"company": filters.company, "account_name": "Sales"}, "name")
	cos_account = frappe.db.get_value("Account", {"company": filters.company, "account_name": "Cost of Sales"}, "name")
	over_heads = frappe.db.get_value("Account", {"company": filters.company, "account_name": "Overheads"}, "name")
	non_operating_account = frappe.db.get_value("Account", {"company": filters.company, "account_name": "Non-Operating Income"}, "name")
	other_expense_account = frappe.db.get_value("Account", {"company": filters.company, "account_name": "Other Expenses"}, "name")

	# frappe.throw(str(sales_account)+"---"+str(cos_account))
	income = get_data(filters.company, "Income", "Credit", period_list, filters = filters,
		accumulated_values=filters.accumulated_values,
		ignore_closing_entries=True, ignore_accumulated_values_for_fy= True, parent_account=sales_account, total_name="Sales")

	expense = get_data(filters.company, "Expense", "Debit", period_list, filters=filters,
		accumulated_values=filters.accumulated_values,
		ignore_closing_entries=True, ignore_accumulated_values_for_fy= True, parent_account=cos_account, total_name="Cost of Sales")

	over_heads = get_data(filters.company, "Expense", "Debit", period_list, filters=filters,
		accumulated_values=filters.accumulated_values,
		ignore_closing_entries=True, ignore_accumulated_values_for_fy= True, parent_account=over_heads, total_name="Overheads")

	non_operating = get_data(filters.company, "Income", "Credit", period_list, filters = filters,
		accumulated_values=filters.accumulated_values,
		ignore_closing_entries=True, ignore_accumulated_values_for_fy= True, parent_account=non_operating_account, total_name="Non-Operating Income")

	other_expense = get_data(filters.company, "Expense", "Debit", period_list, filters=filters,
		accumulated_values=filters.accumulated_values,
		ignore_closing_entries=True, ignore_accumulated_values_for_fy= True, parent_account=other_expense_account, total_name="Other Expenses")

	net_profit_loss = get_net_profit_loss(income, expense, period_list, filters.company, filters.presentation_currency)
	# cos_per = get_cos_per(income, expense, period_list, filters.company, filters.presentation_currency)
	operating_profit = get_operating_profit(income, expense,over_heads, period_list, filters.company, filters.presentation_currency)
	# operating_profit_per = get_operating_profit_per(income, expense,over_heads, period_list, filters.company, filters.presentation_currency)
	final_profit = get_final_profit(income, expense,over_heads,non_operating,other_expense, period_list, filters.company, filters.presentation_currency)
	# final_profit_per = get_final_profit_per(income, expense,over_heads,non_operating,other_expense, period_list, filters.company, filters.presentation_currency)

	data = []
	data.extend(income or [])
	data.extend(expense or [])
	if net_profit_loss:
		data.append(net_profit_loss)
		data.append({})
	# if cos_per:
	# 	data.append(cos_per)
	# 	data.append({})
	data.extend(over_heads or [])
	if operating_profit:
		data.append(operating_profit)
		data.append({})
	# if operating_profit_per:
	# 	data.append(operating_profit_per)
	# 	data.append({})
	data.extend(non_operating or [])
	data.extend(other_expense or [])
	if final_profit:
		data.append(final_profit)
	# if final_profit_per:
	# 	data.append(final_profit_per)

	columns = get_columns(filters.periodicity, period_list, filters.accumulated_values, filters.company)

	# chart = get_chart_data(filters, columns, income, expense, net_profit_loss)

	return columns, data, None

def get_final_profit(income, expense,over_heads,non_operating,other_expense, period_list, company, currency=None, consolidated=False):
	total = 0
	net_profit_loss = {
		"account_name": "'" + _("Net Profit/Loss") + "'",
		"account": "'" + _("Net Profit/Loss") + "'",
		"warn_if_negative": True,
		"currency": currency or frappe.get_cached_value('Company',  company,  "default_currency")
	}

	has_value = False

	for period in period_list:
		key = period if consolidated else period.key
		total_income = flt(income[-2][key], 3) if income else 0
		total_expense = flt(expense[-2][key], 3) if expense else 0
		total_over_heads = flt(over_heads[-2][key], 3) if over_heads else 0
		total_non_operating = flt(non_operating[-2][key], 3) if non_operating else 0
		total_other_expense = flt(other_expense[-2][key], 3) if other_expense else 0
		res = (total_income - total_expense)-total_over_heads
		res+=total_non_operating
		res+=total_other_expense

		net_profit_loss[key] = res

		if net_profit_loss[key]:
			has_value=True

		total += flt(net_profit_loss[key])
		net_profit_loss["total"] = total

	if has_value:
		return net_profit_loss

def get_final_profit_per(income, expense, over_heads,non_operating,other_expense, period_list, company, currency=None, consolidated=False):
	total = 0
	net_profit_loss = {
		"account_name": "'" + _("%") + "'",
		"account": "'" + _("%") + "'",
		"warn_if_negative": True,
		"currency": currency or frappe.get_cached_value('Company',  company,  "default_currency")
	}

	has_value = False

	for period in period_list:
		key = period if consolidated else period.key
		total_income = flt(income[-2][key], 3) if income else 0
		total_expense = flt(expense[-2][key], 3) if expense else 0
		total_over_heads = flt(over_heads[-2][key], 3) if over_heads else 0
		total_non_operating = flt(non_operating[-2][key], 3) if non_operating else 0
		total_other_expense = flt(other_expense[-2][key], 3) if other_expense else 0
		res = (total_income - total_expense)-total_over_heads
		res+=total_non_operating
		res+=total_other_expense

		net_profit_loss[key] = res*100/total_income

		if net_profit_loss[key]:
			has_value=True

		total += flt(net_profit_loss[key])
		net_profit_loss["total"] = total

	if has_value:
		return net_profit_loss

def get_operating_profit(income, expense,over_heads, period_list, company, currency=None, consolidated=False):
	total = 0
	net_profit_loss = {
		"account_name": "'" + _("Operating Profit") + "'",
		"account": "'" + _("Operating Profit") + "'",
		"warn_if_negative": True,
		"currency": currency or frappe.get_cached_value('Company',  company,  "default_currency")
	}

	has_value = False

	for period in period_list:
		key = period if consolidated else period.key
		total_income = flt(income[-2][key], 3) if income else 0
		total_expense = flt(expense[-2][key], 3) if expense else 0
		total_over_heads = flt(over_heads[-2][key], 3) if over_heads else 0

		net_profit_loss[key] = (total_income - total_expense)-total_over_heads

		if net_profit_loss[key]:
			has_value=True

		total += flt(net_profit_loss[key])
		net_profit_loss["total"] = total

	if has_value:
		return net_profit_loss

def get_operating_profit_per(income, expense, over_heads, period_list, company, currency=None, consolidated=False):
	total = 0
	net_profit_loss = {
		"account_name": "'" + _("%") + "'",
		"account": "'" + _("%") + "'",
		"warn_if_negative": True,
		"currency": currency or frappe.get_cached_value('Company',  company,  "default_currency")
	}

	has_value = False

	for period in period_list:
		key = period if consolidated else period.key
		total_income = flt(income[-2][key], 3) if income else 0
		total_expense = flt(expense[-2][key], 3) if expense else 0
		total_over_heads = flt(over_heads[-2][key], 3) if over_heads else 0
		res = (total_income - total_expense)-total_over_heads

		net_profit_loss[key] = res*100/total_income

		if net_profit_loss[key]:
			has_value=True

		total += flt(net_profit_loss[key])
		net_profit_loss["total"] = total

	if has_value:
		return net_profit_loss

def get_net_profit_loss(income, expense, period_list, company, currency=None, consolidated=False):
	total = 0
	net_profit_loss = {
		"account_name": "'" + _("Gross Profit") + "'",
		"account": "'" + _("Gross Profit") + "'",
		"warn_if_negative": True,
		"currency": currency or frappe.get_cached_value('Company',  company,  "default_currency")
	}

	has_value = False

	for period in period_list:
		key = period if consolidated else period.key
		total_income = flt(income[-2][key], 3) if income else 0
		total_expense = flt(expense[-2][key], 3) if expense else 0

		net_profit_loss[key] = total_income - total_expense

		if net_profit_loss[key]:
			has_value=True

		total += flt(net_profit_loss[key])
		net_profit_loss["total"] = total

	if has_value:
		return net_profit_loss

def get_cos_per(income, expense, period_list, company, currency=None, consolidated=False):
	total = 0
	net_profit_loss = {
		"account_name": "'" + _("%") + "'",
		"account": "'" + _("%") + "'",
		# "warn_if_negative": True,
		# "currency": currency or frappe.get_cached_value('Company',  company,  "default_currency")
	}

	has_value = False
	res=0
	total_income=0
	total_expense=0

	for period in period_list:
		key = period if consolidated else period.key
		total_income = flt(income[-2][key], 3) if income else 0
		total_expense = flt(expense[-2][key], 3) if expense else 0
		# res = flt((total_income - total_expense)/total_income)*100 or 0
		# res = get_percentage(total_income - total_expense,total_income)
		# res = (total_income - total_expense)*100/total_income
		total_income+=total_income
		total_expense+=total_expense
		# res1 = res*100
		# res2 = res1/total_income
		# net_profit_loss[key] = (total_income - total_expense)

		# if net_profit_loss[key]:
		# 	has_value=True

		# total += flt(net_profit_loss[key])
		# net_profit_loss["total"] = total
	res = (total_income - total_expense)*100/total_income

	# if has_value:
	net_profit_loss["account_name"] = str(res)+"%"
	net_profit_loss["account"] = str(res)+"%"
	return net_profit_loss

def get_percentage(one,two):
	return (one*100)/two

def get_chart_data(filters, columns, income, expense, net_profit_loss):
	labels = [d.get("label") for d in columns[2:]]

	income_data, expense_data, net_profit = [], [], []

	for p in columns[2:]:
		if income:
			income_data.append(income[-2].get(p.get("fieldname")))
		if expense:
			expense_data.append(expense[-2].get(p.get("fieldname")))
		if net_profit_loss:
			net_profit.append(net_profit_loss.get(p.get("fieldname")))

	datasets = []
	if income_data:
		datasets.append({'name': _('Income'), 'values': income_data})
	if expense_data:
		datasets.append({'name': _('Expense'), 'values': expense_data})
	if net_profit:
		datasets.append({'name': _('Net Profit/Loss'), 'values': net_profit})

	chart = {
		"data": {
			'labels': labels,
			'datasets': datasets
		}
	}

	if not filters.accumulated_values:
		chart["type"] = "bar"
	else:
		chart["type"] = "line"

	chart["fieldtype"] = "Currency"

	return chart