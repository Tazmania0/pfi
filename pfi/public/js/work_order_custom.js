frappe.ui.form.on('Work Order', {
    refresh: function(frm) {
        frm.add_custom_button(__('Auto Generate Cutting Matrix'), function() {
            auto_generate_cutting_matrix(frm);
        });
        frm.add_custom_button(__('Recalculate Planned Qty from Cutting Matrix'), function() {
            recalculate_planned_qty(frm);
        });
    },

    validate: function(frm) {
        validate_cutting_matrix(frm);
    }
});

function validate_cutting_matrix(frm) {
    if (!frm.doc.cutting_matrix) return;

    frm.doc.cutting_matrix.forEach(matrix_row => {
        if (!matrix_row.sizes || matrix_row.sizes.length === 0) {
            frappe.throw(__('Each Cutting Matrix row must have at least one size.'));
        }

        matrix_row.sizes.forEach(size_entry => {
            if (size_entry.quantity <= 0) {
                frappe.throw(__('Quantity must be positive in color {0}, size {1}', [matrix_row.color, size_entry.size]));
            }
            if (size_entry.batch_size <= 0) {
                frappe.throw(__('Batch Size must be positive in color {0}, size {1}', [matrix_row.color, size_entry.size]));
            }
        });
    });
}

function auto_generate_cutting_matrix(frm) {
    if (!frm.doc.planned_qty || frm.doc.planned_qty <= 0) {
        frappe.msgprint(__('Please enter a valid Planned Quantity.'));
        return;
    }

    const colors = ['Red', 'Blue', 'Green']; // Example colors
    const sizes = ['S', 'M', 'L', 'XL']; // Example sizes

    let total_qty = frm.doc.planned_qty;
    let total_combinations = colors.length * sizes.length;
    let qty_per_combination = Math.floor(total_qty / total_combinations);

    frm.clear_table('cutting_matrix');

    colors.forEach(color => {
        let row = frm.add_child('cutting_matrix');
        row.color = color;

        row.sizes = [];
        sizes.forEach(size => {
            row.sizes.push({
                size: size,
                quantity: qty_per_combination,
                batch_size: qty_per_combination
            });
        });
    });

    frm.refresh_field('cutting_matrix');
    frappe.msgprint(__('Cutting Matrix auto-generated.'));
}

function recalculate_planned_qty(frm) {
    if (!frm.doc.cutting_matrix || frm.doc.cutting_matrix.length === 0) {
        frappe.msgprint(__('No Cutting Matrix entries found.'));
        return;
    }

    let total_qty = 0;

    frm.doc.cutting_matrix.forEach(matrix_row => {
        if (matrix_row.sizes && matrix_row.sizes.length > 0) {
            matrix_row.sizes.forEach(size_entry => {
                total_qty += size_entry.quantity || 0;
            });
        }
    });

    frm.set_value('planned_qty', total_qty);
    frappe.msgprint(__('Planned Quantity recalculated from Cutting Matrix.'));
}
