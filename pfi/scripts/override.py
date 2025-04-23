import frappe
from erpnext.manufacturing.doctype.work_order.work_order import WorkOrder as ERPWorkOrder
from pfi.scripts.job_cards import create_job_cards_from_splits

# Preserve the original method
original_create_job_card = ERPWorkOrder.create_job_card

def patched_create_job_card(self):
    original_create_job_card(self)  # Standard ERPNext logic
    frappe.msgprint("Creating Job Cards from Custom Batch Allocation...")
    create_job_cards_from_splits(self.name)

# Apply the patch
ERPWorkOrder.create_job_card = patched_create_job_card
