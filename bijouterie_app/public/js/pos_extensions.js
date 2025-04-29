bijouterie_app.pos.extend_pos_item = function() {
    if (!erpnext.pos || !erpnext.pos.PointOfSale || !erpnext.pos.PointOfSale.prototype.make_item_list) {
        console.warn("PointOfSale.make_item_list not found, skipping extension");
        return;
    }
    
    // Stocker la fonction originale
    const original_make_item_list = erpnext.pos.PointOfSale.prototype.make_item_list;
    
    // Remplacer par notre version étendue
    erpnext.pos.PointOfSale.prototype.make_item_list = function(items) {
        // Appeler la fonction originale
        const result = original_make_item_list.call(this, items);
        
        // Ajouter notre fonctionnalité personnalisée
        // Trouver tous les éléments d'articles et ajouter l'affichage du poids d'or
        this.wrapper.find('.item-card').each(function() {
            const $item = $(this);
            const item_code = $item.attr('data-item-code');
            if (!item_code) return;
            
            const item = items.find(i => i.item_code === item_code);
            if (!item) return;
            
            if (item.gold_weight) {
                const $weight_div = $(`<div class="item-gold-weight">${item.gold_weight} g</div>`);
                $item.find('.item-name').after($weight_div);
            }
        });
        
        return result;
    };
};
