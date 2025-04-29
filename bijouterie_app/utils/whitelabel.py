import frappe

def whitelabel_boot_info(boot_info):
    """
    Modify boot info to apply whitelabel changes
    """
    # Replace app name in boot info
    if boot_info.get("app_name") == "ERPNext":
        boot_info["app_name"] = "Bijouterie"
    
    # Replace app logo
    boot_info["app_logo_url"] = "/assets/bijouterie_app/images/jewelry_logo.svg"
    
    # Replace app version
    if "app_version" in boot_info:
        boot_info["app_version"] = "Bijouterie " + boot_info["app_version"].split(" ")[-1]
    
    # Hide ERPNext modules if configured in settings
    if frappe.db.exists("DocType", "Bijouterie Settings"):
        settings = frappe.get_single("Bijouterie Settings")
        if hasattr(settings, 'hide_erpnext_branding') and settings.hide_erpnext_branding:
            # Apply complete whitelabel
            boot_info["whitelabel"] = {
                "app_name": "Bijouterie",
                "logo_url": "/assets/bijouterie_app/images/jewelry_logo.svg",
                "splash_image": "/assets/bijouterie_app/images/jewelry_logo.svg"
            }
            
            # Hide help menu
            boot_info["help_links"] = []
