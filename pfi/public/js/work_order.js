frappe.ui.form.on('Work Order', {
	before_load: function(frm) {
        // Set default naming series
        if(frm.is_new()) {
            frm.set_value('naming_series', 'MFG-WO-.YYYY.-');
        }
    },

    refresh: function(frm) {
        console.debug("Initializing PFI Work Order customization");
        
        // 1. Allow template items with variants in production_item
        frm.set_query('production_item', () => {
            console.debug("Setting production_item query filter");
            return {
                filters: [
                    ['Item', 'has_variants', '=', 1],
                    ['Item', 'disabled', '=', 0]
                ]
            };
        });

        // 2. Attribute filters for planned quantity table
        frm.set_query('colour', 'planned_quantity_table', () => ({
            filters: {'parent_attribute': 'Colour'}
        }));
        
        frm.set_query('size', 'planned_quantity_table', () => ({
            filters: {'parent_attribute': 'Size'}
        }));

        // 3. Debug current item selection
        if(frm.doc.production_item) {
            console.debug("Current production item:", frm.doc.production_item);
        }
    },

    production_item: function(frm) {
        console.debug("Production item changed to:", frm.doc.production_item);
        if(frm.doc.production_item) {
            frm.call('validate_template_item')
                .fail(() => {
                    console.warn("Invalid template item, resetting field");
                    frm.set_value('production_item', '');
                });
        }
    }
});