import frappe
from frappe import _
from frappe.model.document import Document
from erpnext.manufacturing.doctype.work_order.work_order import WorkOrder

def validate_template_item(doc):
    """Validate selected item is a proper template with required attributes"""
    if not doc.production_item:
        return

    item = frappe.get_doc("Item", doc.production_item)
    
    if not item.has_variants:
        frappe.throw(
            _("Selected item must be a Template with variants"),
            title=_("Invalid Item Selection"),
            exc=frappe.ValidationError
        )
    
    required_attributes = {'Colour', 'Size'}
    existing_attributes = {attr.attribute for attr in item.attributes}
    
    missing = required_attributes - existing_attributes
    if missing:
        frappe.throw(
            _("Missing required attributes: {0}").format(", ".join(missing)),
            title=_("Template Configuration Error"),
            exc=frappe.ValidationError
        )

def validate_planned_quantities(doc):
    """Validate planned quantity table entries"""
    seen = set()
    for row in doc.planned_quantity_table:
        # Check duplicate combinations
        key = (row.colour, row.size)
        if key in seen:
            frappe.throw(_("Duplicate Colour-Size in row #{0}").format(row.idx))
        seen.add(key)
        
        # Validate variant exists
        variant = get_variant(doc.production_item, row.colour, row.size)
        if not variant:
            frappe.throw(_("Variant not found for Colour {0}, Size {1}").format(row.colour, row.size))
            
        # Validate quantities
        if row.cut_quantity > row.planned_quantity:
            frappe.throw(_("Row #{0}: Cut Qty cannot exceed Planned Qty").format(row.idx))

def sync_cutting_matrix(doc):
    """Sync cutting matrix with planned quantity table"""
    doc.cutting_matrix_table = []
    for row in doc.planned_quantity_table:
        doc.append("cutting_matrix_table", {
            "colour": row.colour,
            "size": row.size,
            "quantity": row.cut_quantity
        })

def get_variant(template, colour, size):
    """Get variant item from template and attributes"""
    return frappe.get_value("Item", {
        "variant_of": template,
        "attributes": [
            ["Item Variant Attribute", "attribute", "=", "Colour"],
            ["Item Variant Attribute", "attribute_value", "=", colour],
            ["Item Variant Attribute", "attribute", "=", "Size"],
            ["Item Variant Attribute", "attribute_value", "=", size]
        ]
    }, "name")

def before_save(doc, method):
    """Enhanced validation chain"""
    # New validations
    validate_template_item(doc)
    validate_planned_quantities(doc)
    sync_cutting_matrix(doc)
    
    # Original validations
    validate_cutting_matrix(doc)
    recalculate_planned_qty(doc)
    validate_bom_is_service_bom(doc)

def generate_job_cards(doc):
    """Job card creation with preserved batch threshold logic"""
    if doc.docstatus != 1:
        return

    job_card_data = []
    default_batch_size = get_batch_size(doc)
    use_small_batch_rules = not doc.cutting_matrix_table and default_batch_size < 10

    for entry in doc.planned_quantity_table:
        remaining_qty = entry.planned_quantity - entry.cut_quantity
        if remaining_qty <= 0:
            continue
            
        variant = get_variant(doc.production_item, entry.colour, entry.size)
        
        # Preserve original batch threshold logic
        if use_small_batch_rules:
            batch_size = remaining_qty
            batches = 1
        else:
            batch_size = default_batch_size
            batches = calculate_batches(remaining_qty, batch_size)
        for batch_idx in range(batches):
            qty = calculate_batch_qty(remaining_qty, batch_size, batch_idx)
            job_card_data.append({
                'work_order': doc.name,
                'production_item': variant,
                'for_quantity': qty,
                'planned_qty': remaining_qty,
                'color': entry.colour,
                'size': entry.size,
                'customer_po': doc.customer_po,
                'batch_index': f"{batch_idx + 1}/{batches}" if batches > 1 else None
            })

    # Original creation logic
    for data in job_card_data:
        job_card = frappe.get_doc({'doctype': 'Job Card', **data})
        job_card.insert(ignore_permissions=True)
        frappe.msgprint(_("Created Job Card {0}").format(job_card.name))
# Original helper functions (keep unchanged)
def validate_cutting_matrix(doc):
    if doc.cutting_matrix_table:
        for entry in doc.cutting_matrix_table:
            if entry.quantity <= 0:
                frappe.throw(_("Quantity must be positive for Color {0}").format(entry.color))
            if not entry.size:
                frappe.throw(_("Size is mandatory for all Cutting Matrix entries"))

def recalculate_planned_qty(doc):
    if doc.cutting_matrix_table:
        doc.planned_qty = sum(entry.quantity for entry in doc.cutting_matrix_table)
    elif doc.planned_quantity_table:
        doc.planned_qty = sum(entry.planned_quantity for entry in doc.planned_quantity_table)

def validate_bom_is_service_bom(doc):
    if doc.bom_no:
        bom = frappe.get_doc("BOM", doc.bom_no)
        if bom.is_service_bom and bom.items:
            frappe.throw(_("BOM {0} is marked as service but contains items").format(bom.name))

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


def on_submit(doc, method):
    generate_job_cards(doc)

def activate_work_order_overrides():
    """Explicitly apply Work Order overrides after migration"""
    from erpnext.manufacturing.doctype.work_order.work_order import WorkOrder
    WorkOrder.before_save = before_save
    WorkOrder.on_submit = on_submit
    frappe.msgprint("PFI Work Order overrides activated")
    

# Monkey-patch Work Order hooks
WorkOrder.before_save = before_save
WorkOrder.on_submit = on_submit
