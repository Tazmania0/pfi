frappe.ui.form.on('Batch Allocation', {
    batch_qty: function(frm, cdt, cdn) {
        console.log("Batch Qty changed");
        auto_fill_remaining_qty(frm, cdt, cdn);
    },

    batch_allocation_add: function(frm, cdt, cdn) {
        console.log("New Batch Allocation row added");
        prefill_remaining_qty(frm, cdt, cdn);
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

    // If user has entered a value, add it to the sum and validate
    const current_qty = row.batch_qty || 0;
    const total_with_current = sum + current_qty;

    if (total_with_current > total_qty) {
        frappe.msgprint(__('Total allocated quantity exceeds the Work Order quantity.'));
    }

    // Only auto-fill if field is empty or 0
    if (!row.batch_qty || row.batch_qty === 0) {
        const remaining = total_qty - sum;
        if (remaining > 0) {
            frappe.model.set_value(cdt, cdn, 'batch_qty', remaining);
        } else {
            frappe.msgprint(__('All quantity has already been allocated to batches.'));
        }
    }
}


// Used only for autofilling empty new rows
function prefill_remaining_qty(frm, cdt, cdn) {
    const row = locals[cdt][cdn];
    if (!row.batch_qty) {
        auto_fill_remaining_qty(frm, cdt, cdn);
    }
}