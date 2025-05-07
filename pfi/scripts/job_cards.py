import frappe
from frappe.model.document import Document

class CustomJobCard:
    @staticmethod
    def validate(doc):
        #Add debug log entering in custom Job card validate
        #frappe.msgprint("Debug: Entering CustomJobCard.validate")
        CustomJobCard.ensure_quantity_does_not_exceed_work_order(doc)
        CustomJobCard.ensure_valid_quantity(doc)

    @staticmethod
    def ensure_quantity_does_not_exceed_work_order(doc):
        #Add debug log entering in custom Job card validate
        #frappe.msgprint("Debug: Entering CustomJobCard.ensure_quantity_does_not_exceed_work_order")
        if not doc.work_order:
            return

        wo = frappe.get_doc("Work Order", doc.work_order)
        overproduction_percentage = frappe.db.get_single_value(
            "Manufacturing Settings", "overproduction_percentage_for_work_order"
        ) or 0

        allowed_qty = wo.qty * (1 + overproduction_percentage / 100)

        # Only count job cards for the first operation
        operation = doc.operation
        job_cards = frappe.get_all(
            "Job Card",
            filters={
                "work_order": doc.work_order,
                "operation": operation,
                "name": ("!=", doc.name)
            },
            pluck="name"
        )
        existing_qty = sum(
            frappe.db.get_value("Job Card", jc, "for_quantity") or 0
            for jc in job_cards
        )

        total_with_current = existing_qty + (doc.for_quantity or 0)
        if total_with_current > allowed_qty:
            frappe.throw(
                f"Total Job Card quantity for operation '{operation}' "
                f"({total_with_current}) exceeds allowed Work Order quantity including overproduction ({allowed_qty})."
            )
    @staticmethod
    def ensure_valid_quantity(doc):
        if not doc.for_quantity or not isinstance(doc.for_quantity, (int, float)):
            frappe.throw("Job Card Quantity (for_quantity) must be a number.")
        if doc.for_quantity <= 0 or doc.for_quantity != int(doc.for_quantity):
            frappe.throw("Job Card Quantity (for_quantity) must be a positive integer.")

def validate_batch_allocations(work_order, method=None):
    """Ensure batch allocations do not exceed Work Order qty + Overproduction%"""
    total_batch_qty = sum(row.batch_qty for row in work_order.batch_allocations)
    overproduction_percentage = frappe.db.get_single_value("Manufacturing Settings", "overproduction_percentage_for_work_order") or 0
    allowed_qty = work_order.qty * (1 + overproduction_percentage / 100)

    if total_batch_qty > allowed_qty:
        frappe.throw(
            f"Total batch allocation ({total_batch_qty}) exceeds allowed quantity to manufacture including overproduction ({allowed_qty})."
        )

        
        
#@frappe.whitelist()
#def create_job_cards_from_splits(work_order_name):
#    work_order = frappe.get_doc("Work Order", work_order_name)
#    frappe.msgprint("Calling Validate batch allocations..")
#    validate_batch_allocations(work_order)
#    for row in work_order.batch_allocations:
#        if row.status != "Pending":
#            continue
#        job_card = frappe.new_doc("Job Card")
#        job_card.work_order = work_order.name
#        job_card.for_quantity = row.batch_qty
#        job_card.operation = work_order.operations[0].operation  # Customize if multiple ops
#        job_card.save()
#        row.status = "Created"
#    work_order.save()
#    return "Job Cards Created"


# Validate wrapper to be called from hooks

def validate_job_card(doc, method):
    #Add debug log entering in custom Job card validate
    #frappe.msgprint("Debug: Entering validate_job_card (to run CustomJobCard.validate)")
    CustomJobCard.validate(doc)
    
    
    
# In Job Card Doctype:
# Use existing field:
# Fieldname: for_quantity
# Fieldtype: Int
# Description: This field is already present and used for job card quantity.

# Create a Doctype: Batch Allocation
# Fields:
# - batch_qty (Int, Required)
# - status (Select: [Pending, Created], Default: Pending)

# Add a Child Table in Work Order:
# - Label: Batch Allocations
# - Fieldname: batch_allocations
# - Options: Batch Allocation

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint, flt
from erpnext.manufacturing.doctype.work_order.work_order import WorkOrder as ERPNextWorkOrder
from erpnext.manufacturing.doctype.work_order.work_order import split_qty_based_on_batch_size

class WorkOrder(ERPNextWorkOrder):
    def create_job_card(self):
        manufacturing_settings_doc = frappe.get_doc("Manufacturing Settings")

        enable_capacity_planning = not cint(manufacturing_settings_doc.disable_capacity_planning)
        plan_days = cint(manufacturing_settings_doc.capacity_planning_for_days) or 30

        # Custom batch logic: check if batch allocations exist
        if self.batch_allocations:  # 'batch_allocations' is the table field in Work Order
            frappe.msgprint("Creating Job Cards from Custom Batch allocations...")
            self.create_job_cards_from_batch_allocations(plan_days, enable_capacity_planning)
        else:
            # Default ERPNext logic
            for index, row in enumerate(self.operations):
                qty = self.qty
                while qty > 0:
                    qty = split_qty_based_on_batch_size(self, row, qty)
                    if row.job_card_qty > 0:
                        self.prepare_data_for_job_card(row, index, plan_days, enable_capacity_planning)

        planned_end_date = self.operations and self.operations[-1].planned_end_time
        if planned_end_date:
            self.db_set("planned_end_date", planned_end_date)

    def create_job_cards_from_batch_allocations(self, plan_days, enable_capacity_planning):
        for batch in self.batch_allocations:
            if batch.status != "Pending":
                continue

            for index, row in enumerate(self.operations):
                if batch.batch_qty > 0:
                    temp_qty = batch.batch_qty
                    while temp_qty > 0:
                        temp_qty = split_qty_based_on_batch_size(self, row, temp_qty)
                        if row.job_card_qty > 0:
                            row.job_card_qty = batch.batch_qty
                            #self.prepare_data_for_job_card(row, index, plan_days, enable_capacity_planning)
                            self.prepare_data_for_job_card_batchwise(row, index, plan_days, enable_capacity_planning)

            batch.status = "Created"

        planned_end_date = self.operations and self.operations[-1].planned_end_time
        if planned_end_date:
            self.db_set("planned_end_date", planned_end_date)


    
    
    #Time calcaulation fix 
    def prepare_data_for_job_card_batchwise(self, row, index, plan_days, enable_capacity_planning):
        from copy import deepcopy
        from erpnext.manufacturing.doctype.work_order.work_order import create_job_card as create_job_card_standalone

        #from frappe.utils.data import flt
        
        # Work on a copy of the row to prevent modifying original operation
        local_row = deepcopy(row)

        # Adjust time proportionally to the job_card_qty (which reflects batch qty)
        if float(self.qty):
            local_row.time_in_mins = max(
                1,
                float(row.time_in_mins) * float(row.job_card_qty) / float(self.qty)
            )
        else:
            local_row.time_in_mins = row.time_in_mins

        # Use same logic as ERPNext to calculate time range
        self.set_operation_start_end_time(index, local_row)

        # Create job card with adjusted time
        job_card_doc = create_job_card_standalone(self,
                local_row, auto_create=True, enable_capacity_planning=enable_capacity_planning
        )

        # Update planning info if enabled
        if enable_capacity_planning and job_card_doc:
            local_row.planned_start_time = job_card_doc.scheduled_time_logs[-1].from_time
            local_row.planned_end_time = job_card_doc.scheduled_time_logs[-1].to_time

            if date_diff(local_row.planned_end_time, self.planned_start_date) > plan_days:
                frappe.message_log.pop()
                frappe.throw(
                    _(
                        "Unable to find the time slot in the next {0} days for the operation {1}. "
                        "Please increase the 'Capacity Planning For (Days)' in the {2}."
                    ).format(
                        plan_days,
                        local_row.operation,
                        get_link_to_form("Manufacturing Settings", "Manufacturing Settings"),
                    ),
                    CapacityError,
                )

            local_row.db_update()
            
