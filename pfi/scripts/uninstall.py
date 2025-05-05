import frappe

def remove_custom_reports():
    report_name = "Executions - f2"
    try:
        frappe.delete_doc("Report", report_name, force=True)
        frappe.db.commit()
        frappe.logger().info(f"Removed custom report: {report_name}")
    except frappe.DoesNotExistError:
        frappe.logger().info(f"Report {report_name} does not exist. Skipping.")
    except Exception as e:
        frappe.logger().error(f"Failed to remove report {report_name}: {e}")
