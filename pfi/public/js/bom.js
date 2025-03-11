frappe.ui.form.on('BOM', {
    refresh: function(frm) {
        toggle_items_table(frm);
    },
    is_service_bom: function(frm) {
        toggle_items_table(frm);
    }
});

function toggle_items_table(frm) {
    if (frm.doc.is_service_bom) {
        frm.set_df_property('items', 'hidden', 1);
        frm.fields_dict.items.grid.wrapper.hide();
    } else {
        frm.set_df_property('items', 'hidden', 0);
        frm.fields_dict.items.grid.wrapper.show();
    }
}