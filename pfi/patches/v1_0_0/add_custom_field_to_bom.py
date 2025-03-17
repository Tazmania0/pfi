import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def execute():
    # Define the custom field
    custom_fields = {
        "BOM": [
            {
                "fieldname": "pfi_notes",
                "label": "PFI Notes",
                "fieldtype": "Small Text",
                "insert_after": "with_operations",
                "hidden": 1,
                "read_only": 1,
            }
        ]
    }

    try:
        # Check if the field exists and matches desired properties
        existing_field = frappe.db.get_value(
            "Custom Field",
            {"fieldname": "pfi_notes", "dt": "BOM"},
            ["name", "fieldtype", "label", "hidden", "read_only"],
            as_dict=True
        )

        if not existing_field:
            # Create the field if it doesn't exist
            create_custom_fields(custom_fields)
            frappe.msgprint("Custom field 'pfi_notes' created successfully.")
        else:
            # Update properties if they don't match
            needs_update = (
                existing_field.fieldtype != "Small Text"
                or existing_field.label != "PFI Notes"
                or existing_field.hidden != 1
                or existing_field.read_only != 1
            )
            if needs_update:
                frappe.db.set_value(
                    "Custom Field",
                    existing_field.name,
                    {
                        "fieldtype": "Small Text",
                        "label": "PFI Notes",
                        "hidden": 1,
                        "read_only": 1,
                        "insert_after": "with_operations"
                    }
                )
                frappe.msgprint("Custom field 'pfi_notes' updated successfully.")

    except Exception as e:
        frappe.log_error(f"Failed to create/update custom field: {str(e)}")
        raise e