frappe.ui.form.on('Work Order', {
    batch_allocations_add: function(frm, cdt, cdn) {
        const new_row = locals[cdt][cdn];

        // Calculate sum of all previous batches
        let total = 0;
        (frm.doc.batch_allocations || []).forEach(row => {
            if (row.name !== new_row.name && row.batch_qty) {
                total += flt(row.batch_qty);
            }
        });

        const remaining = flt(frm.doc.qty) - total;

        if (remaining > 0) {
            frappe.model.set_value(cdt, cdn, 'batch_qty', remaining);
        } else {
            frappe.msgprint(__('All quantity already allocated.'));
        }
    }
});
