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


frappe.ui.form.on('Work Order', {
    refresh: function(frm) {
        update_batch_allocation_summary(frm);
    },
    batch_allocations_on_form_rendered: function(frm) {
        update_batch_allocation_summary(frm);
    },
    batch_allocations_add: function(frm) {
        update_batch_allocation_summary(frm);
    },
    batch_allocations_remove: function(frm) {
        update_batch_allocation_summary(frm);
    }
});


function update_batch_allocation_summary(frm) {
    let total_allocated = 0;
    (frm.doc.batch_allocations || []).forEach(row => {
        total_allocated += flt(row.batch_qty);
    });

    let overproduction_percentage = flt(frappe.defaults.get_default("overproduction_percentage_for_work_order")) || 0;
    let allowed_qty = flt(frm.doc.qty) * (1 + overproduction_percentage / 100);
    let remaining_qty = allowed_qty - total_allocated;

    let summary_html = `<div style="padding: 8px; background-color: #f7f7f7; border: 1px solid #d1d8dd; border-radius: 4px;">
        <strong>Total Allocated:</strong> ${total_allocated} / ${allowed_qty} (Remaining: ${remaining_qty})
    </div>`;

    frm.fields_dict.batch_allocation_summary.$wrapper.html(summary_html);
}