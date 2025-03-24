app_name = "pfi"
app_title = "PFI"
app_publisher = "PFI"

app_description = "Custom ERPNext App for Garment Manufacturing and Job Card Customization"
#app_icon = "octicon octicon-file-directory"
app_color = "gray"
app_email = "your@email.com"

app_license = "MIT"

#app_version = "1.0.0"

# Apps
# ------------------

# required_apps = []

# Include JS only if file exists
app_include_js = [
    "assets/pfi/js/work_order.js"
]

doc_events = {
#    "Work Order": {
#        "before_submit": "pfi.custom_scripts.work_order_custom.before_submit_work_order"
#    },
#    "Work Order": {
#
#        "validate": "pfi.work_order_custom.validate_work_order"
#
#    },
#    "Work Order": {
#        "before_save": "pfi.custom_scripts.work_order_validate.before_save"
#    } 
}

doc_events = {
#    "Work Order": {
#        "before_save": "pfi.custom_scripts.work_order_customization.before_save",
#        "on_submit": "pfi.custom_scripts.work_order_customization.on_submit"
#    }
}

doc_events = {
#    "BOM": {
#        "before_validate": "pfi.custom_scripts.bom_events.validate_bom"
#    }
}

# hooks.py
override_doctype_class = {
    "BOM": "pfi.custom_scripts.bom_service_check.CustomBOM",
    "Work Order": "pfi.custom_scripts.work_order_custom.CustomWorkOrder"
}

include_js = [
    "public/js/pfi.js",
    "public/js/JsBarcode.all.min.js" 
]

fixtures = [
#    {"dt": "Custom Field", "filters": [["module", "=", "PFI"]]},
#    {"dt": "Property Setter", "filters": [["module", "=", "PFI"]]},
    "Custom Field",
#    "Cutting Matrix Table",
#    "Planned Quantity Table",
    "Print Format/Job Card A8"
]


# Include JS for Work Order and Job Card (client-side logic)

doctype_js = {
#    "Work Order": "public/js/work_order_custom.js",
#    "Cutting Matrix Table": "doctype/manufacturing/cutting_matrix_table/cutting_matrix_table.js",
#    "Size Table": "doctype/manufacturing/size_table/size_table.js",
    "BOM": "public/js/bom.js"

#    "Job Card": "public/js/job_card_custom.js"

}

after_migrate = [
    # Existing BOM patch
    "pfi.patches.v1_0_0.add_custom_field_to_bom.execute"
    # New Work Order override activation
    #"pfi.work_order_custom.activate_work_order_overrides"
    "pfi.patches.v1_0_0.set_naming_defaults.execute"
]



# hooks.py
from frappe import _

def get_data():
    return {
        # App metadata
        "app_name": "pfi",
        "app_title": "PFI",
        "app_description": "Custom ERPNext App for Garment Manufacturing and Job Card Customization",
        
        # Define your module(s)
        "modules": [
            {
                "label": _("PFI"),  # Display name
                "items": ["Cutting Matrix Table", "Planned Quantity Table" ]  # List DocTypes/pages in this module
            }
        ],
        
        # Other hooks (fixtures, doctype_js, etc.)
        "doctype_js": {"BOM": "public/js/bom.js"},
        "fixtures": ["Custom Field", "Print Format"]
    }

def after_migrate():
    from frappe import reload_doctype
    reload_doctype("Work Order")
    frappe.publish_realtime('msgprint', 'Work Order overrides reloaded')