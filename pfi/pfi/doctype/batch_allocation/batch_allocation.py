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
    
    # Create Job Cards
    work_order_doc = frappe.get_doc("Work Order", work_order)
    frappe.db.delete("Job Card", {"work_order": work_order})
    
    for batch in batches:
        job_card = frappe.get_doc({
            "doctype": "Job Card",
            "work_order": work_order,
            "production_item": work_order_doc.production_item,
            "bom_no": work_order_doc.bom_no,
            "for_quantity": batch.get("batch_size"),
            "company": work_order_doc.company,
            "posting_date": frappe.utils.nowdate()
        })
        job_card.insert(ignore_permissions=True)
    
    return True

@frappe.whitelist()
def get_allocations(work_order):
    return frappe.get_all("Batch Allocation",
        filters={"work_order": work_order},
        fields=["name", "batch_size"]
    )