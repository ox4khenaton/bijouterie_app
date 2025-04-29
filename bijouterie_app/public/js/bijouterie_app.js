// Namespace pour l'application bijouterie
frappe.provide('bijouterie_app');
frappe.provide('bijouterie_app.pos');

// Initialisation
bijouterie_app.init = function() {
    // Initialiser les extensions POS si elles existent
    if (typeof erpnext !== 'undefined' && erpnext.pos) {
        bijouterie_app.pos.extend_pos_item();
        bijouterie_app.pos.extend_barcode_mass_printing();
    }
    
    // Ajouter des hooks pour les événements globaux
    $(document).on('app_ready', function() {
        console.log('Bijouterie App initialized');
    });
};

// Exécuter l'initialisation quand Frappe est prêt
$(document).ready(function() {
    bijouterie_app.init();
});
