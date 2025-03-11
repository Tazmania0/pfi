// pfi/public/js/bom.js
frappe.ui.form.on('BOM', {
    refresh: function(frm) {
        // Initialize visibility of "Is Service" and Items table
        frm.toggle_display('is_service_bom', frm.doc.with_operations);
        frm.toggle_display('items', !frm.doc.is_service_bom);
        
        // Clear Items table if "Is Service" is checked
        if (frm.doc.is_service_bom) {
            frm.clear_table('items');
            frm.refresh_field('items');
        }
		frm.events.toggle_items_requirement(frm);
    },
    with_operations: function(frm) {
        // Toggle "Is Service" visibility and reset if needed
        frm.toggle_display('is_service_bom', frm.doc.with_operations);
        if (!frm.doc.with_operations && frm.doc.is_service_bom) {
            frm.set_value('is_service_bom', 0);
        }
    },
    is_service_bom: function(frm) {
        // Clear Items table and hide it
		frm.events.toggle_items_requirement(frm);
        frm.toggle_display('items', !frm.doc.is_service_bom);
        if (frm.doc.is_service_bom) {
            frm.clear_table('items');
            frm.refresh_field('items');
        }
    },
	toggle_items_requirement: function(frm) {
        // Dynamically set items requirement
        frm.set_df_property('items', 'reqd', !frm.doc.is_service_bom);
        frm.toggle_display('items', !frm.doc.is_service_bom);
    }
  


});