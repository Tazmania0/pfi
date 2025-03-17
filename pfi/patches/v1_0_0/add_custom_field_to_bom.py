# add_custom_field_to_bom.py
import frappe

def execute():
    frappe.reload_doctype("BOM")
    create_custom_field()

def create_custom_field():
    fieldname = "is_service_bom"
    
    # Check if field already exists
    if not frappe.db.exists("Custom Field", 
        {"dt": "BOM", "fieldname": fieldname}):
        
        custom_field = {
            "dt": "BOM",
            "label": "Is Service",
            "fieldname": fieldname,
            "fieldtype": "Check",
            "insert_after": "with_operations",  # Now placed below "With Operations"
            "description": "Check if this BOM is for a service (non-stock item)."
        }
        
        frappe.get_doc({
            "doctype": "Custom Field",
            **custom_field
        }).insert(ignore_permissions=True)
        
        frappe.msgprint(f"Created custom field '{fieldname}' in BOM")
    else:
        frappe.msgprint(f"Custom field '{fieldname}' already exists in BOM - Skipping creation")
