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

// Used only for autofilling empty new rows
function prefill_remaining_qty(frm, cdt, cdn) {
    const row = locals[cdt][cdn];
    if (!row.batch_qty) {
        auto_fill_remaining_qty(frm, cdt, cdn);
    }
}