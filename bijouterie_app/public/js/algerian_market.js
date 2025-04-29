// Add Algerian market customizations
$(document).ready(function() {
    // Add support for Algerian Dinar currency format
    frappe.model.currency_format_map = frappe.model.currency_format_map || {};
    frappe.model.currency_format_map.DZD = "#,###.## DA";
    
    // Set default currency to Algerian Dinar if not set
    if (!frappe.defaults.get_default("currency")) {
        frappe.defaults.set_default("currency", "DZD");
    }
    
    // Add Arabic language support
    if (!$('link[href*="noto-sans-arabic"]').length) {
        $('head').append('<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Arabic:wght@400;700&family=Noto+Naskh+Arabic&display=swap" rel="stylesheet">');
    }
    
    // Add common Algerian gold weights and measurements
    frappe.provide("bijouterie_app.algerian");
    bijouterie_app.algerian = {
        // Common gold weights in Algeria (in grams)
        common_weights: [1.5, 2, 3, 5, 8, 10, 18, 21],
        
        // Gold purity standards in Algeria
        gold_standards: [
            {label: "18K (75%)", value: 18},
            {label: "21K (87.5%)", value: 21},
            {label: "24K (99.9%)", value: 24}
        ],
        
        // Apply Algerian market defaults to forms
        apply_defaults: function(frm) {
            if (frm.doc.doctype === "Item" && frm.doc.item_group === "Or") {
                // Default to 18K gold which is common in Algeria
                if (!frm.doc.gold_carat) {
                    frm.set_value("gold_carat", 18);
                }
            }
        }
    };
    
    // Hook into form load events
    frappe.ui.form.on('Item', {
        refresh: function(frm) {
            bijouterie_app.algerian.apply_defaults(frm);
        }
    });
    
    // Add Algerian holidays to calendar
    var algerian_holidays = [
        {date: "01-01", title: "Nouvel An"},
        {date: "05-01", title: "Fête du Travail"},
        {date: "07-05", title: "Journée du Savoir"},
        {date: "05-07", title: "Fête de l'Indépendance"},
        {date: "01-11", title: "Fête de la Révolution"}
        // Islamic holidays would be added dynamically as they change yearly
    ];
    
    // Apply holidays to calendar views
    if (frappe.views && frappe.views.Calendar) {
        frappe.provide("frappe.views.Calendar.prototype.original_render_events");
        frappe.views.Calendar.prototype.original_render_events = frappe.views.Calendar.prototype.render_events;
        frappe.views.Calendar.prototype.render_events = function() {
            this.original_render_events();
            var me = this;
            
            // Add Algerian holidays
            var today = new Date();
            var year = today.getFullYear();
            
            $.each(algerian_holidays, function(i, holiday) {
                var date_parts = holiday.date.split('-');
                var holiday_date = new Date(year, parseInt(date_parts[1])-1, parseInt(date_parts[0]));
                
                me.events.push({
                    start: holiday_date,
                    end: holiday_date,
                    title: holiday.title,
                    color: '#006233' // Algerian green
                });
            });
            
            me.cal.addEventSource(me.events);
        };
    }
});
