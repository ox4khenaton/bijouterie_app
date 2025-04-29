app_name = "bijouterie_app"
app_title = "Bijouterie App"
app_publisher = "Manus"
app_description = "Application personnalisée pour bijouterie algérienne spécialisée dans l'or 18 carats"
app_email = "support@manus.ai"
app_license = "MIT"
app_icon = "octicon octicon-gem"
app_color = "gold"

# Completely restructured for ERPNext 15 compatibility
app_include_js = ["/assets/bijouterie_app/js/bijouterie_app.bundle.js"]
app_include_css = ["/assets/bijouterie_app/css/bijouterie_app.bundle.css"]

doctype_js = {
    "Item": ["public/js/item.js"]
}

doc_events = {
    "Item": {
        "validate": ["bijouterie_app.utils.item_hooks.validate_gold_item"]
    }
}

fixtures = [
    {"dt": "Custom Field", "filters": [["module", "=", "Bijouterie App"]]},
    {"dt": "Custom Script", "filters": [["module", "=", "Bijouterie App"]]},
    {"dt": "Property Setter", "filters": [["module", "=", "Bijouterie App"]]}
]

# Hook to hide modules based on Bijouterie Settings
on_session_creation = [
    "bijouterie_app.utils.module_visibility.hide_modules",
]

# Apply whitelabel changes to boot info
extend_bootinfo = "bijouterie_app.utils.whitelabel.whitelabel_boot_info"

# Also hide modules and apply whitelabel when settings are updated
doc_events.update({
    "Bijouterie Settings": {
        "on_update": [
            "bijouterie_app.utils.module_visibility.hide_modules",
        ]
    }
})

# Override standard web pages
website_context = {
    "favicon": "/assets/bijouterie_app/images/jewelry_logo.svg",
    "app_name": "Bijouterie",
    "app_title": "Bijouterie",
    "app_logo_url": "/assets/bijouterie_app/images/jewelry_logo.svg",
}

# Override login page
web_include_css = [
    "/assets/bijouterie_app/css/jewelry_theme.css"
]

# Override email templates
email_brand_image = "/assets/bijouterie_app/images/jewelry_logo.svg"
