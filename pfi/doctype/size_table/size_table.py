import frappe
from frappe.model.document import Document

class SizeTable(Document):
    def validate(self):
        if self.planned_quantity < 0:
            frappe.throw("Planned Quantity must be positive.")