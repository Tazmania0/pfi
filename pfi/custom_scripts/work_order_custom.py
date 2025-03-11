import frappe
from frappe import _
from frappe.model.document import Document

@frappe.whitelist()
def before_save(doc, method):
    validate_cutting_matrix(doc)
    recalculate_planned_qty(doc)
    validate_bom_is_service(doc)

@frappe.whitelist()
def validate_cutting_matrix(doc):
    if doc.cutting_matrix:
        for matrix_row in doc.cutting_matrix:
            if not matrix_row.sizes:
                frappe.throw(f"Color '{matrix_row.color}' missing sizes.")
            
            for size in matrix_row.sizes:
                if size.quantity <= 0:
                    frappe.throw(f"Quantity in color '{matrix_row.color}', size '{size.size}' must be positive.")
                if size.batch_size <= 0:
                    frappe.throw(f"Batch size in color '{matrix_row.color}', size '{size.size}' must be positive.")

@frappe.whitelist()
def recalculate_planned_qty(doc):
    if not doc.cutting_matrix: return
    
    total_qty = 0
    for matrix_row in doc.cutting_matrix:
        for size in matrix_row.sizes:
            total_qty += size.quantity or 0
    doc.planned_qty = total_qty

@frappe.whitelist()
def validate_bom_is_service(doc):
    if doc.bom_no:
        bom_doc = frappe.get_doc("BOM", doc.bom_no)
        if bom_doc.is_service and bom_doc.items:
            frappe.throw(f"BOM '{bom_doc.name}' is marked as service but contains raw materials.")

@frappe.whitelist()
def on_submit(doc, method):
    generate_job_cards(doc)



@frappe.whitelist()
def generate_job_cards(work_order):
    wo = frappe.get_doc("Work Order", work_order)

    if wo.docstatus != 1:
        frappe.throw(_("Only submitted Work Orders are allowed."))

    job_card_data = []

    # 1. Cutting Matrix takes precedence
    if wo.get("cutting_matrix_table"):
        frappe.msgprint(_("Generating Job Cards from Cutting Matrix..."))
        for entry in wo.cutting_matrix_table:
            if entry.quantity <= 0 or entry.batch_size <= 0:
                frappe.throw(_("Cutting Matrix entries must have positive Quantity and Batch Size."))

            batches = -(-entry.quantity // entry.batch_size) # Ceiling division

            for batch in range(batches):
                qty = min(entry.batch_size, entry.quantity - batch * entry.batch_size)
                job_card_data.append({
                    'operation': wo.operations[0].operation if wo.operations else "",
                    'work_order': wo.name,
                    'planned_qty': qty,
                    'cutting_matrix_ref': entry.name
                })

    # 2. If no Cutting Matrix, use Planned Quantity
    elif wo.planned_qty > 0:
        frappe.msgprint(_("Generating Job Cards from Planned Quantity..."))
        default_batch_size = frappe.db.get_single_value("Manufacturing Settings", "default_job_card_batch_size") or 10

        batches = -(-wo.planned_qty // default_batch_size)

        for batch in range(batches):
            qty = min(default_batch_size, wo.planned_qty - batch * default_batch_size)
            job_card_data.append({
                'operation': wo.operations[0].operation if wo.operations else "",
                'work_order': wo.name,
                'planned_qty': qty
            })

    # 3. Fallback to BOM Batch Size
    elif wo.bom_no:
        frappe.msgprint(_("Generating Job Cards from BOM Batch Size..."))
        bom = frappe.get_doc("BOM", wo.bom_no)
        batch_size = bom.batch_size or 1
        qty_remaining = wo.qty

        batches = -(-qty_remaining // batch_size)

        for batch in range(batches):
            qty = min(batch_size, qty_remaining - batch * batch_size)
            job_card_data.append({
                'operation': wo.operations[0].operation if wo.operations else "",
                'work_order': wo.name,
                'planned_qty': qty
            })

    else:
        frappe.throw(_("No data found for Job Card generation!"))

    # Create Job Cards
    for data in job_card_data:
        job_card = frappe.new_doc("Job Card")
        job_card.update({
            'work_order': data['work_order'],
            'operation': data['operation'],
            'qty': data['planned_qty']
        })
        job_card.insert(ignore_permissions=True)
        frappe.db.commit()

    return True

