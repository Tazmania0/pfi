frappe.ui.form.on('Batch Allocation', {
    batch_qty: function(frm, cdt, cdn) {
        console.log("Batch Qty changed");
        auto_fill_remaining_qty(frm, cdt, cdn);
    }
});

frappe.ui.form.on('Batch Allocation', {
    grid_setup: function(frm) {
		console.log("Entering grid setup function");
        if (frm.fields_dict.batch_allocations && frm.fields_dict.batch_allocations.grid) {
            frm.fields_dict.batch_allocations.grid.on('add_row', function(grid_row) {
                const row = grid_row.doc;
                const total_qty = frm.doc.qty || 0;

                let sum = 0;
                (frm.doc.batch_allocations || []).forEach(b => {
                    if (b.name !== row.name && b.batch_qty) {
                        sum += b.batch_qty;
                    }
                });

                const remaining = total_qty - sum;
                if (remaining > 0) {
                    row.batch_qty = remaining;
                    frm.refresh_field("batch_allocations");
                    console.log("Auto-filled new batch_qty with:", remaining);
                } else {
                    frappe.msgprint(__('All quantity has already been allocated to batches.'));
                }
            });
        }
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
    if (remaining > 0) {
        frappe.model.set_value(cdt, cdn, 'batch_qty', remaining);
    } else {
        frappe.msgprint(__('All quantity has already been allocated to batches.'));
    }
}
