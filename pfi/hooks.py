from frappe import _

app_name = "pfi"
app_title = "PFI"
app_publisher = "PFI"

app_description = "Custom ERPNext App for Garment Manufacturing and Job Card Customization"
app_icon = "octicon octicon-file-directory"
app_color = "gray"
app_email = "your@email.com"

app_license = "MIT"

app_version = "1.0.0"

doc_events = {
    "Work Order": {
        "before_submit": "pfi.custom_scripts.work_order_custom.before_submit_work_order"
    },
    "BOM": {
        "validate": "pfi.custom_scripts.bom_service_check.validate_bom",
        "before_submit": "pfi.custom_scripts.bom_service_check.before_submit_bom"
    },
    "Work Order": {

        "validate": "pfi.work_order_custom.validate_work_order"

    },
    "Work Order": {
        "before_save": "pfi.custom_scripts.work_order_validate.before_save"
    } 
}
fixtures = ["Custom Field", "Print Format"]

app_include_js = "public/js/work_order_custom.js"
app_include_css = "public/css/work_order.css"

# Include JS for Work Order and Job Card (client-side logic)

doctype_js = {

    "Work Order": "public/js/work_order_custom.js",
    "Cutting Matrix Table": "doctype/manufacturing/cutting_matrix_table/cutting_matrix_table.js",
    "Size Table": "doctype/manufacturing/size_table/size_table.js",
    "BOM": "public/js/bom.js"

#    "Job Card": "public/js/job_card_custom.js"

}