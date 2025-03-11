frappe.ui.form.on('Cutting Matrix Table', {
    quantity: function (frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (row.quantity < 0) {
            frappe.msgprint(__('Quantity must be a positive number.'));
            frappe.model.set_value(cdt, cdn, 'quantity', 0);
        }
    },
    batch_size: function (frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (row.batch_size < 0) {
            frappe.msgprint(__('Batch Size must be a positive number.'));
            frappe.model.set_value(cdt, cdn, 'batch_size', 0);
        }
    }
});