frappe.ui.form.on('Work Order', {
    onload: function(frm) {
        console.log("Work Order form loaded");
    },

    batch_allocations_add: function(frm, cdt, cdn) {
        console.log("New batch row added");
        auto_fill_remaining_qty(frm, cdt, cdn);
    }
});

frappe.ui.form.on('Batch Allocation', {
    batch_qty: function(frm, cdt, cdn) {
        console.log("Batch Qty changed");
        // Optional: validate or recalculate something here
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


frappe.ui.form.on('Work Order', {
    onload: function(frm) {
        // Attach handler to batch_allocations grid after form loads
        frm.fields_dict["batch_allocations"].grid.on("add_row", function(grid_row) {
            let row = grid_row.doc;

            // Calculate total allocated quantity from existing rows
            let total_allocated = 0;
            (frm.doc.batch_allocations || []).forEach(r => {
                if (r.name !== row.name) {
                    total_allocated += r.batch_qty || 0;
                }
            });

            let remaining = frm.doc.qty - total_allocated;
            console.log("New row added. Remaining qty:", remaining);

            if (remaining > 0) {
                frappe.model.set_value(row.doctype, row.name, "batch_qty", remaining);
            }
        });
    }
});
