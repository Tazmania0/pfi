def execute():
    # Set default naming series in Manufacturing Settings
    if not frappe.db.get_value("Manufacturing Settings", "Manufacturing Settings", "default_work_order_naming_series"):
        frappe.db.set_value("Manufacturing Settings", "Manufacturing Settings", 
            "default_work_order_naming_series", "MFG-WO-.YYYY.-")
    
    # Ensure Work Order doctype uses naming series
    if frappe.db.get_value("DocType", "Work Order", "autoname") != "naming_series:":
        frappe.db.set_value("DocType", "Work Order", "autoname", "naming_series:")