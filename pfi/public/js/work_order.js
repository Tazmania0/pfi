frappe.ui.form.on('Work Order', {
    refresh: function(frm) {
        // Template item filtering
        frm.set_query('production_item', function() {
            return {
                filters: {
                    'has_variants': 1,
                    'disabled': 0
                }
            };
        });

        // Attribute filters for planned quantity table
        frm.set_query('colour', 'planned_quantity_table', function() {
            return { filters: { parent_attribute: 'Colour' } };
        });
        
        frm.set_query('size', 'planned_quantity_table', function() {
            return { filters: { parent_attribute: 'Size' } };
        });
    },

    production_item: function(frm) {
        // Trigger template validation
        if(frm.doc.production_item) {
            frm.call('validate_template_item').fail(() => {
                frm.set_value('production_item', '');
            });
        }
    }
});