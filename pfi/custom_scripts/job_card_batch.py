import frappe
from pfi.custom_scripts.cutting_matrix import process_cutting_matrix

@frappe.whitelist()
def create_batches_from_cutting_matrix(work_order_name):
    work_order = frappe.get_doc("Work Order", work_order_name)
    matrix = work_order.get("cutting_matrix", [])
    
    if matrix:
        batches = process_cutting_matrix(matrix)
    else:
        batches = [{
            "color": "N/A",
            "size": "N/A",
            "quantity": work_order.planned_qty,
            "batch_size": work_order.batch_size or work_order.planned_qty
        }]

    for batch in batches:
        job_card = frappe.get_doc({
            "doctype": "Job Card",
            "work_order": work_order.name,
            "operation": work_order.operations[0].operation,
            "batch_size": batch["batch_size"]
        })
        job_card.insert()
        frappe.msgprint(f"Job Card created for {batch['color']} - {batch['size']}")
