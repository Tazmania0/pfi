import frappe
from frappe.model.document import Document

class BatchAllocation(Document):
    def validate(self):
        if self.batch_size < 1:
            frappe.throw("Batch Size must be at least 1")

@frappe.whitelist()
def create_allocations(work_order, batches):
    # Clear existing allocations
    frappe.db.delete("Batch Allocation", {"work_order": work_order})
    
    # Create new allocations
    for batch in batches:
        doc = frappe.get_doc({
            "doctype": "Batch Allocation",
            "work_order": work_order,
            "batch_size": batch.get("batch_size")
        })
        doc.insert(ignore_permissions=True)
    
    # Create job cards
    work_order_doc = frappe.get_doc("Work Order", work_order)
    frappe.db.delete("Job Card", {"work_order": work_order})
    
    for batch in batches:
        job_card = frappe.get_doc({
            "doctype": "Job Card",
            "work_order": work_order,
            "production_item": work_order_doc.production_item,
            "bom_no": work_order_doc.bom_no,
            "for_quantity": batch.get("batch_size"),
            "company": work_order_doc.company
        })
        job_card.insert(ignore_permissions=True)
    
    return len(batches)