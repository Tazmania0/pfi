import frappe
from frappe import _
from frappe.model.document import Document
from erpnext.manufacturing.doctype.work_order.work_order import WorkOrder

def validate_cutting_matrix(doc):
    if doc.cutting_matrix_table:
        for entry in doc.cutting_matrix_table:
            if entry.quantity <= 0:
                frappe.throw(_("Quantity must be positive for Color {0}").format(entry.color))
            if not entry.size:
                frappe.throw(_("Size is mandatory for all Cutting Matrix entries"))

def recalculate_planned_qty(doc):
    """Update main planned_qty from active table"""
    if doc.cutting_matrix_table:
        doc.planned_qty = sum(entry.quantity for entry in doc.cutting_matrix_table)
    elif doc.planned_quantity_table:
        doc.planned_qty = sum(entry.planned_qty for entry in doc.planned_quantity_table)

def validate_bom_is_service_bom(doc):
    if doc.bom_no:
        bom = frappe.get_doc("BOM", doc.bom_no)
        if bom.is_service_bom and bom.items:
            frappe.throw(_("BOM {0} is marked as service but contains items").format(bom.name))

def generate_job_cards(doc):
    if doc.docstatus != 1:
        return

    job_card_data = []
    
    # Priority 1: Cutting Matrix Table
    if doc.cutting_matrix_table:
        frappe.msgprint(_("Creating Job Cards from Cutting Matrix..."))
        for entry in doc.cutting_matrix_table:
            job_card_data.append({
                'work_order': doc.name,
                'production_item': doc.production_item,
                'for_quantity': entry.quantity,
                'planned_qty': entry.quantity,
                'color': entry.color,
                'size': entry.size,
                'customer_po': doc.customer_po
            })
    
    # Priority 2: Planned Quantity Table
    elif doc.planned_quantity_table:
        frappe.msgprint(_("Creating Job Cards from Planned Quantity..."))
        default_batch_size = get_batch_size(doc)
        
        for entry in doc.planned_quantity_table:
            # Apply special case for small batches without cutting matrix
            if not doc.cutting_matrix_table and default_batch_size < 10:
                batch_size = entry.planned_qty
            else:
                batch_size = default_batch_size
            
            batches = calculate_batches(entry.planned_qty, batch_size)
            
            for batch_idx in range(batches):
                qty = calculate_batch_qty(entry.planned_qty, batch_size, batch_idx)
                job_card_data.append({
                    'work_order': doc.name,
                    'production_item': doc.production_item,
                    'for_quantity': qty,
                    'planned_qty': entry.planned_qty,
                    'color': entry.color,
                    'size': entry.size,
                    'customer_po': doc.customer_po,
                    'batch_index': f"{batch_idx + 1}/{batches}"
                })
    
    # Priority 3: BOM Batch Size
    else:
        frappe.msgprint(_("Creating Job Cards from BOM Batch Size..."))
        batch_size = get_batch_size(doc)
        
        # Apply special case for small batches without cutting matrix
        if not doc.cutting_matrix_table and batch_size < 10:
            batch_size = doc.planned_qty
        
        batches = calculate_batches(doc.planned_qty, batch_size)
        
        for batch_idx in range(batches):
            qty = calculate_batch_qty(doc.planned_qty, batch_size, batch_idx)
            job_card_data.append({
                'work_order': doc.name,
                'production_item': doc.production_item,
                'for_quantity': qty,
                'planned_qty': doc.planned_qty,
                'customer_po': doc.customer_po,
                'batch_index': f"{batch_idx + 1}/{batches}"
            })

    # Create Job Cards
    for data in job_card_data:
        job_card = frappe.get_doc({
            'doctype': 'Job Card',
            **data
        })
        job_card.insert(ignore_permissions=True)
        frappe.msgprint(_("Created Job Card {0}").format(job_card.name))

def get_batch_size(doc):
    return (
        frappe.db.get_value("BOM", doc.bom_no, "batch_size") 
        or frappe.db.get_single_value("Manufacturing Settings", "default_job_card_batch_size") 
        or 1
    )

def calculate_batches(total_qty, batch_size):
    return max(1, -(-total_qty // batch_size))  # Ceiling division with min 1 batch

def calculate_batch_qty(total_qty, batch_size, batch_idx):
    return min(batch_size, total_qty - batch_idx * batch_size)

def before_save(doc, method):
    validate_cutting_matrix(doc)
    recalculate_planned_qty(doc)
    validate_bom_is_service_bom(doc)

def on_submit(doc, method):
    generate_job_cards(doc)

# Monkey-patch Work Order hooks
WorkOrder.before_save = before_save
WorkOrder.on_submit = on_submit