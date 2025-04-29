frappe.ui.form.on('Achat Or Usagé', {
    refresh: function(frm) {
        frm.add_custom_button(__('Calculer les montants'), function() {
            calculate_amounts(frm);
        });
        
        if (frm.doc.docstatus === 1) {
            frm.add_custom_button(__('Créer entrée de stock'), function() {
                frappe.call({
                    method: 'bijouterie_app.bijouterie_app.doctype.achat_or_usage.achat_or_usage.create_stock_entry',
                    args: {
                        'doc_name': frm.doc.name
                    },
                    callback: function(r) {
                        if (r.message) {
                            frappe.show_alert({
                                message: __('Entrée de stock créée: ' + r.message),
                                indicator: 'green'
                            }, 5);
                        }
                    }
                });
            });
        }
    },
    validate: function(frm) {
        calculate_amounts(frm);
    }
});

frappe.ui.form.on('Achat Or Usagé Item', {
    gold_carat: function(frm, cdt, cdn) {
        calculate_row_amount(frm, cdt, cdn);
    },
    weight: function(frm, cdt, cdn) {
        calculate_row_amount(frm, cdt, cdn);
    },
    gold_items_remove: function(frm) {
        calculate_totals(frm);
    }
});

function calculate_row_amount(frm, cdt, cdn) {
    var row = locals[cdt][cdn];
    
    // Définir le facteur de pureté en fonction des carats
    var purity_factors = {
        '24': 1.0,
        '22': 0.916,
        '21': 0.875,
        '18': 0.750,
        '14': 0.585,
        '9': 0.375
    };
    
    row.purity_factor = purity_factors[row.gold_carat] || 0;
    
    // Récupérer le prix actuel de l'or
    frappe.call({
        method: 'frappe.client.get_list',
        args: {
            doctype: 'Cours de l\'Or',
            fields: ['price_per_gram'],
            filters: {},
            order_by: 'date desc',
            limit: 1
        },
        callback: function(r) {
            if (r.message && r.message.length > 0) {
                var gold_price = r.message[0].price_per_gram;
                
                // Calculer le prix d'achat (généralement 70-80% du prix de vente)
                var purchase_factor = 0.75; // 75% du prix de vente
                row.price_per_gram = gold_price * row.purity_factor * purchase_factor;
                
                // Calculer le montant
                row.amount = row.weight * row.price_per_gram;
                
                refresh_field('gold_items');
                calculate_totals(frm);
            }
        }
    });
}

function calculate_amounts(frm) {
    $.each(frm.doc.gold_items || [], function(i, item) {
        calculate_row_amount(frm, item.doctype, item.name);
    });
}

function calculate_totals(frm) {
    var total_weight = 0;
    var total_amount = 0;
    
    $.each(frm.doc.gold_items || [], function(i, item) {
        total_weight += item.weight;
        total_amount += item.amount;
    });
    
    frm.set_value('total_weight', total_weight);
    frm.set_value('total_amount', total_amount);
}
