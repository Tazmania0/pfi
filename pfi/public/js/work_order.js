frappe.ui.form.on('Work Order', {
    refresh: function(frm) {
        // Show allocation button only for draft orders
        if (frm.doc.docstatus === 0) {
            frm.add_custom_button(__('Allocate Batches'), () => show_batch_dialog(frm));
        }

        // Refresh allocations table
        frm.fields_dict.batch_allocations.grid.refresh();
    },

    // Automatically fetch linked allocations
    batch_allocations: function(frm) {
        if (!frm.doc.__islocal) {
            frappe.db.get_list('Batch Allocation', {
                filters: { work_order: frm.doc.name },
                fields: ['name', 'batch_size']
            }).then(entries => {
                frm.doc.batch_allocations = entries;
                frm.refresh_field('batch_allocations');
            });
        }
    }
});

function show_batch_dialog(frm) {
    const dialog = new frappe.ui.Dialog({
        // ... [keep previous dialog setup] ...
    });

    dialog.set_primary_action(__('Save & Submit'), async () => {
        // ... [keep validation logic] ...
        
        await frappe.call({
            method: 'pfi.pfi.doctype.batch_allocation.batch_allocation.create_allocations',
            args: {
                work_order: frm.doc.name,
                batches: batches
            },
            callback: () => {
                // Refresh allocations table after creation
                frm.doc.batch_allocations = [];
                frm.trigger('batch_allocations');
            }
        });

        dialog.hide();
        frm.save().then(() => frm.submit());
    });

    dialog.show();
}