bijouterie_app.pos.extend_barcode_mass_printing = function() {
    if (!erpnext.pos || !erpnext.pos.PointOfSale || !erpnext.pos.PointOfSale.prototype.make_control_panel) {
        console.warn("PointOfSale.make_control_panel not found, skipping extension");
        return;
    }
    
    // Stocker la fonction originale
    const original_make_control_panel = erpnext.pos.PointOfSale.prototype.make_control_panel;
    
    // Remplacer par notre version étendue
    erpnext.pos.PointOfSale.prototype.make_control_panel = function() {
        // Appeler la fonction originale
        const result = original_make_control_panel.call(this);
        
        // Ajouter notre bouton d'impression en masse
        const $button_container = this.wrapper.find('.page-actions');
        if ($button_container.length) {
            const $print_button = $(`
                <div class="btn-group">
                    <button class="btn btn-default btn-sm print-all-barcodes">
                        <i class="fa fa-barcode"></i> ${__('Imprimer tous les codes-barres')}
                    </button>
                </div>
            `);
            
            $button_container.append($print_button);
            
            // Ajouter l'événement d'impression
            $print_button.on('click', () => {
                this.print_all_barcodes();
            });
        }
        
        // Ajouter la méthode d'impression en masse
        this.print_all_barcodes = function() {
            const me = this;
            const dialog = new frappe.ui.Dialog({
                title: __('Imprimer les codes-barres'),
                fields: [
                    {
                        fieldname: 'item_group',
                        label: __('Groupe d\'articles'),
                        fieldtype: 'Link',
                        options: 'Item Group',
                        default: 'Or'
                    },
                    {
                        fieldname: 'print_format',
                        label: __('Format d\'impression'),
                        fieldtype: 'Link',
                        options: 'Print Format',
                        filters: {
                            'doc_type': 'Item'
                        },
                        default: 'Barcode Label'
                    }
                ],
                primary_action: function() {
                    const values = dialog.get_values();
                    frappe.call({
                        method: 'frappe.client.get_list',
                        args: {
                            doctype: 'Item',
                            fields: ['name'],
                            filters: {
                                'item_group': values.item_group
                            }
                        },
                        callback: function(r) {
                            if (r.message && r.message.length) {
                                const item_names = r.message.map(item => item.name);
                                frappe.call({
                                    method: 'frappe.printing.doctype.print_format.print_format.download_multi_pdf',
                                    args: {
                                        doctype: 'Item',
                                        name: item_names,
                                        format: values.print_format
                                    }
                                });
                            } else {
                                frappe.msgprint(__('Aucun article trouvé dans ce groupe'));
                            }
                        }
                    });
                    dialog.hide();
                }
            });
            dialog.show();
        };
        
        return result;
    };
};
