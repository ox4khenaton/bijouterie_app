import frappe

def whitelabel_boot_info(bootinfo):
    """
    Modify boot info to apply whitelabel changes
    """
    # Replace app name in boot info
    if bootinfo.get("app_name") == "ERPNext":
        bootinfo["app_name"] = "Bijouterie"
    
    # Replace app logo
    bootinfo["app_logo_url"] = "/assets/bijouterie_app/images/jewelry_logo.svg"
    
    # Replace app version
    if "app_version" in bootinfo:
        bootinfo["app_version"] = "Bijouterie " + bootinfo["app_version"].split(" ")[-1]
    
    # Hide ERPNext modules if configured in settings
    if frappe.db.exists("DocType", "Bijouterie Settings"):
        settings = frappe.get_single("Bijouterie Settings")
        if hasattr(settings, 'hide_erpnext_branding') and settings.hide_erpnext_branding:
            # Apply complete whitelabel
            bootinfo["whitelabel"] = {
                "app_name": "Bijouterie",
                "logo_url": "/assets/bijouterie_app/images/jewelry_logo.svg",
                "splash_image": "/assets/bijouterie_app/images/jewelry_logo.svg"
            }
            
            # Hide help menu
            bootinfo["help_links"] = []
