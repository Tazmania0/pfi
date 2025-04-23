# Monkey patching the on_submit job card logic 


def override_create_job_card():
    from erpnext.manufacturing.doctype.work_order.work_order import WorkOrder as ERPWorkOrder

    original_method = ERPWorkOrder.create_job_card

    def patched_create_job_card(self):
        original_method(self)
        frappe.msgprint("Creating Job Cards from Custom Batch Allocation...")
        from pfi.scripts.job_cards import create_job_cards_from_splits
        create_job_cards_from_splits(self.name)

    ERPWorkOrder.create_job_card = patched_create_job_card
