import frappe
from frappe import _

def validate_bom(doc, method):
    # Check if the BOM is marked as service-only
    if doc.get("is_service_bom"):
        # Ensure no raw materials exist in the BOM Items table
        if doc.items:
            frappe.throw(_("This BOM is marked as 'Service Only' and cannot have raw materials. Please remove all items."))
    else:
        # Optionally: enforce that a non-service BOM must have at least one item or throw a warning
        if not doc.items and not doc.get("is_service_bom"):
            frappe.msgprint(_("This BOM has no raw materials and is not marked as 'Service Only'. Please review."))

def before_submit_bom(doc, method):
    # Additional check on submit
    if doc.get("is_service_bom") and doc.items:
        frappe.throw(_("Cannot submit BOM with raw materials when marked as 'Service Only'. Remove all items."))


