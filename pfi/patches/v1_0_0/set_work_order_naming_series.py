import frappe


def execute():
    frappe.db.set_value("DocType", "Work Order", "autoname", "naming_series:")