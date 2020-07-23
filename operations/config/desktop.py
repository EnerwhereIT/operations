# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"module_name": "Operations",
			"category": "Modules",
			"color": "#FFE133",
			"icon": "octicon octicon-database",
			"type": "module",
			"label": _("Operations"),
			"description": "Automating invoices, maintaining plants, meter readings,..."
		}
	]
