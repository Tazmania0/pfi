frappe.ui.form.on('Work Order', {
    onload: function (frm) {
        // You can also attach triggers here if needed
		frappe.msgprint(__('Custom JS loaded.'));
    },

    batch_allocations_add: function (frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        const total_qty = frm.doc.qty || 0;

        // Sum existing batch_qty values
        let sum_of_batches = 0;
        (frm.doc.batch_allocations || []).forEach(b => {
            if (b.name !== row.name && b.batch_qty) {
                sum_of_batches += b.batch_qty;
            }
        });

        // Fill in the remaining qty
        let remaining = total_qty - sum_of_batches;
        if (remaining > 0) {
            frappe.model.set_value(cdt, cdn, 'batch_qty', remaining);
        } else {
            frappe.msgprint(__('All quantity has already been allocated to batches.'));
        }
    }
});
