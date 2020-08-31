from __future__ import unicode_literals
import frappe,erpnext,operations
from frappe.model.document import Document
def execute():
    doc = frappe.new_doc('Meter Reading')
    doc.serial_no = 'CS3U-375MB-AG'
    doc.plant = 'Frank2'
    doc.insert()
