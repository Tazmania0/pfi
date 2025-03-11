import frappe
from frappe.model.document import Document

class CuttingMatrixTable(Document):
    def validate(self):
        if self.quantity < 0:
            frappe.throw("Quantity must be positive.")
        if self.batch_size < 0:
            frappe.throw("Batch Size must be positive.")

