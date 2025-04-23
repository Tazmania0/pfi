import frappe
from frappe.model.document import Document

class CustomJobCard:
    @staticmethod
    def validate(doc):
        CustomJobCard.ensure_quantity_does_not_exceed_work_order(doc)
        CustomJobCard.ensure_valid_quantity(doc)

    @staticmethod
    def ensure_quantity_does_not_exceed_work_order(doc):
        if not doc.work_order:
            return

        wo = frappe.get_doc("Work Order", doc.work_order)
        existing_qty = sum(
            frappe.db.get_value("Job Card", jc, "for_quantity") or 0
            for jc in frappe.get_all("Job Card", filters={"work_order": doc.work_order, "name": ("!=", doc.name)}, pluck="name")
        )
        allowed_qty = wo.qty * (1 + (wo.overproduction_percentage or 0) / 100)

        if existing_qty + (doc.for_quantity or 0) > allowed_qty:
            frappe.throw(f"Total Job Card quantity ({existing_qty + (doc.for_quantity or 0)}) exceeds allowed Work Order quantity including overproduction ({allowed_qty}).")

    @staticmethod
    def ensure_valid_quantity(doc):
        if not doc.for_quantity or not isinstance(doc.for_quantity, (int, float)):
            frappe.throw("Job Card Quantity (for_quantity) must be a number.")
        if doc.for_quantity <= 0 or doc.for_quantity != int(doc.for_quantity):
            frappe.throw("Job Card Quantity (for_quantity) must be a positive integer.")

def validate_batch_allocations(work_order, method=None):
    """Ensure batch allocations do not exceed Work Order qty + Overproduction%"""
    total_batch_qty = sum(row.batch_qty for row in work_order.batch_allocations)
    overproduction = getattr(work_order, "overproduction_percentage", 0) or 0
    allowed_qty = work_order.qty * (1 + overproduction / 100)

    if total_batch_qty > allowed_qty:
        frappe.throw(
            f"Total batch allocation ({total_batch_qty}) exceeds allowed quantity to manufacture including overproduction ({allowed_qty})."
        )
        
        
@frappe.whitelist()
def create_job_cards_from_splits(work_order_name):
    work_order = frappe.get_doc("Work Order", work_order_name)
    validate_batch_allocations(work_order)
    for row in work_order.batch_allocations:
        if row.status != "Pending":
            continue
        job_card = frappe.new_doc("Job Card")
        job_card.work_order = work_order.name
        job_card.for_quantity = row.batch_qty
        job_card.operation = work_order.operations[0].operation  # Customize if multiple ops
        job_card.save()
        row.status = "Created"
    work_order.save()
    return "Job Cards Created"


# Validate wrapper to be called from hooks

def validate_job_card(doc, method):
    CustomJobCard.validate(doc)

# In Job Card Doctype:
# Use existing field:
# Fieldname: for_quantity
# Fieldtype: Int
# Description: This field is already present and used for job card quantity.

# Create a Doctype: Batch Allocation
# Fields:
# - batch_qty (Int, Required)
# - status (Select: [Pending, Created], Default: Pending)

# Add a Child Table in Work Order:
# - Label: Batch Allocations
# - Fieldname: batch_allocations
# - Options: Batch Allocation
