frappe.ui.form.on('Size Table', {
    planned_quantity: function (frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (row.planned_quantity < 0) {
            frappe.msgprint(__('Planned Quantity must be a positive number.'));
            frappe.model.set_value(cdt, cdn, 'planned_quantity', 0);
        }
    }
});