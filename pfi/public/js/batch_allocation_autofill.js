frappe.ui.form.on('Batch Allocation', {
    batch_qty: function(frm, cdt, cdn) {
    	// Ensure this runs only once per row addition
        if (!locals[cdt][cdn].__batch_qty_initialized) {
            // Your batch quantity logic
            console.log("Batch Qty changed");
        	auto_fill_remaining_qty(frm, cdt, cdn);
			
            // Set flag to prevent duplicate execution
            locals[cdt][cdn].__batch_qty_initialized = true;
        } 
		update_batch_allocation_summary(frm);	
    },
	status_remove: function(frm, cdt, cdn) {
			 console.log("Batch Qty removed");
			 update_batch_allocation_summary(frm);
	},
	before_status_remove: function(frm, cdt, cdn) {
			 console.log("Batch Qty to be removed");
			 update_batch_allocation_summary(frm);
	}
});
	
	
	
	
	


function auto_fill_remaining_qty(frm, cdt, cdn) {
    const row = locals[cdt][cdn];
    const total_qty = frm.doc.qty || 0;

    let sum = 0;
    (frm.doc.batch_allocations || []).forEach(b => {
        if (b.name !== row.name && b.batch_qty) {
            sum += b.batch_qty;
        }
    });

    const remaining = total_qty - sum;

    // If value already exists, validate it
    if (row.batch_qty && row.batch_qty > 0) {
        const total_with_current = sum + row.batch_qty;
        if (total_with_current > total_qty) {
            const exceeded = total_with_current - total_qty;
            frappe.msgprint(__('Total allocated quantity exceeds the Work Order quantity by {0}.', [exceeded]));
        }
        return;
    }

    // Otherwise, suggest the remaining value
    if (remaining > 0) {
        frappe.msgprint(__('Suggested Batch Qty: {0}', [remaining]));
    } else {
        frappe.msgprint(__('All quantity has already been allocated to batches.'));
    }
}

frappe.ui.form.on('Work Order', {
    onload(frm) {
        console.log("WORKORDER: onload!");
		update_batch_allocation_summary(frm);
    },
	refresh: function(frm) {
	
        console.log("WORKORDER: refresh!");
	 // Initialize flag to check if handler is already attached
        if (!frm._qtyHandlerAttached) {
            frm.trigger('qty');
            frm._qtyHandlerAttached = true;
        }
		update_batch_allocation_summary(frm);
    },
	qty(frm) {
		 console.log("WORKORDER: qty!");
        	update_batch_allocation_summary(frm);
    }

});


function update_batch_allocation_summary(frm) {
    let total_allocated = 0;
    (frm.doc.batch_allocations || []).forEach(row => {
        total_allocated += flt(row.batch_qty);
    });

    const overproduction_percentage = flt(frappe.sys_defaults.overproduction_percentage_for_work_order) || 0;
    const allowed_qty = flt(frm.doc.qty) * (1 + overproduction_percentage / 100);
    const remaining_qty = allowed_qty - total_allocated;

    const html = `
        <div style="padding: 8px; background: #f5f7fa; border: 1px solid #d1d8dd; border-radius: 4px; margin-bottom: 10px;">
            <div style="display: flex; justify-content: space-between; align-items: center">
                <div>
	    	    <strong>Batch Allocation Summary:</strong><br>
		    Allocated: <strong>${total_allocated}</strong> / Allowed: <strong>${allowed_qty}</strong>
		    (${remaining_qty >= 0 ? 'Remaining' : 'Exceeded'}: <strong style="color: ${remaining_qty >= 0 ? 'green' : 'red'}">${remaining_qty}</strong>)
        	</div>
		<button class="btn btn-default btn-xs recalculate-batch-summary" type="button" 
                    style="margin-left: 10px; align-self: flex-end">
                    ${__('Recalculate')}
                </button>
            </div>
        </div>
    `;

    if (frm.fields_dict.batch_allocation_summary) {
        frm.fields_dict.batch_allocation_summary.$wrapper.html(html);
        
        // Add click handler for the recalculate button
        frm.fields_dict.batch_allocation_summary.$wrapper.off('click', '.recalculate-batch-summary')
            .on('click', '.recalculate-batch-summary', function() {
                update_batch_allocation_summary(frm);
            });
    }
}

