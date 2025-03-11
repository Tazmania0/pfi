import frappe
from frappe.model.document import Document

def validate_cutting_matrix(doc, method):
    # Ensure cutting matrix exists if set
    if doc.cutting_matrix:
        for matrix_row in doc.cutting_matrix:
            if not matrix_row.sizes:
                frappe.throw(f"Cutting Matrix row '{matrix_row.color}' is missing size entries.")
            
            for size_entry in matrix_row.sizes:
                if size_entry.quantity <= 0:
                    frappe.throw(f"Quantity for color '{matrix_row.color}', size '{size_entry.size}' must be positive.")
                
                if size_entry.batch_size <= 0:
                    frappe.throw(f"Batch Size for color '{matrix_row.color}', size '{size_entry.size}' must be positive.")

def before_save(doc, method):
    validate_cutting_matrix(doc, method)

