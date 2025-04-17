frappe.ui.form.on('Work Order', {
    refresh: function(frm) {
        // Button for draft orders
        if (frm.doc.docstatus === 0) {
            frm.add_custom_button(__('Allocate Batches'), () => show_batch_dialog(frm));
        }

        // Load and display existing allocations
        if (!frm.doc.__islocal) {
            frappe.call({
                method: 'pfi.pfi.doctype.batch_allocation.batch_allocation.get_allocations',
                args: { work_order: frm.doc.name },
                callback: (r) => {
                    const html = `<div class="alert alert-info">
                        ${r.message.map(a => `Batch ${a.name}: ${a.batch_size}`).join('<br>')}
                    </div>`;
                    frm.fields_dict.batch_allocations_html.$wrapper.html(html || 'No allocations found');
                }
            });
        }
    }
});

function show_batch_dialog(frm) {
    const dialog = new frappe.ui.Dialog({
        title: __('Batch Allocation'),
        fields: [
            {
                fieldtype: 'HTML',
                fieldname: 'info',
                options: `<div class="alert alert-info">Total Quantity: ${frm.doc.qty}</div>`
            },
            {
                fieldtype: 'Table',
                fieldname: 'batches',
                label: __('Batches'),
                fields: [{
                    fieldtype: 'Int',
                    label: __('Batch Size'),
                    fieldname: 'batch_size',
                    reqd: 1,
                    minvalue: 1
                }]
            }
        ]
    });

    dialog.set_primary_action(__('Save & Submit'), async () => {
        const batches = dialog.get_values().batches;
        const total = batches.reduce((sum, row) => sum + (row.batch_size || 0), 0);
        
        if (total !== frm.doc.qty) {
            frappe.throw(__("Total batches must equal Work Order quantity ({0})", [frm.doc.qty]));
            return;
        }

        await frappe.call({
            method: 'pfi.pfi.doctype.batch_allocation.batch_allocation.create_allocations',
            args: {
                work_order: frm.doc.name,
                batches: batches
            },
            freeze: true,
            callback: () => frm.refresh()
        });

        dialog.hide();
        frm.save().then(() => frm.submit());
    });

    dialog.show();
}