frappe.ui.form.on('Item', {
    refresh: function(frm) {
        // Ajouter des fonctionnalités spécifiques aux bijoux en or
        if (frm.doc.item_group && frm.doc.item_group.includes('Or')) {
            frm.add_custom_button(__('Calculer prix selon cours'), function() {
                calculate_gold_price(frm);
            });
        }
    },
    
    gold_weight: function(frm) {
        calculate_gold_price(frm);
    },
    
    gold_carat: function(frm) {
        calculate_gold_price(frm);
    }
});

function calculate_gold_price(frm) {
    if (!frm.doc.gold_weight || !frm.doc.gold_carat) {
        frappe.msgprint(__('Veuillez spécifier le poids et les carats de l\'or'));
        return;
    }
    
    frappe.call({
        method: 'frappe.client.get_list',
        args: {
            doctype: 'Cours de l\'Or',
            fields: ['price_per_gram', 'margin_percentage'],
            filters: {},
            order_by: 'date desc',
            limit: 1
        },
        callback: function(r) {
            if (r.message && r.message.length > 0) {
                let gold_price = r.message[0].price_per_gram;
                let margin = r.message[0].margin_percentage;
                
                // Définir le facteur de pureté en fonction des carats
                let purity_factors = {
                    '24': 1.0,
                    '22': 0.916,
                    '21': 0.875,
                    '18': 0.750,
                    '14': 0.585,
                    '9': 0.375
                };
                
                let purity_factor = purity_factors[frm.doc.gold_carat] || 0.750; // Par défaut 18 carats
                
                // Calculer le prix final
                let base_price = frm.doc.gold_weight * gold_price * purity_factor;
                let margin_amount = base_price * (margin / 100);
                let final_price = base_price + margin_amount;
                
                // Mettre à jour le prix standard
                frm.set_value('standard_rate', final_price);
                
                frappe.show_alert({
                    message: __(`Prix calculé: ${final_price.toFixed(2)} (Cours: ${gold_price}, Poids: ${frm.doc.gold_weight}g, Carats: ${frm.doc.gold_carat}K)`),
                    indicator: 'green'
                }, 5);
            } else {
                frappe.msgprint(__('Aucun cours de l\'or trouvé. Veuillez d\'abord définir le cours de l\'or.'));
            }
        }
    });
}
