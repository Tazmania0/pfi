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

    const current_qty = row.batch_qty || 0;
    const remaining = total_qty - sum;

    // Warn if exceeding
    if (sum + current_qty > total_qty) {
        frappe.msgprint(__('Total allocated quantity exceeds the Work Order quantity.'));
    }

    // Suggest the remaining value only if current field is empty or 0
    if (!row.batch_qty || row.batch_qty === 0) {
        if (remaining > 0) {
            frappe.msgprint(__('Suggested Batch Qty: {0}', [remaining]));
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