import frappe

def hide_modules():
    """
    Hide unnecessary modules in ERPNext based on settings in Bijouterie Settings
    """
    if not frappe.db.exists("DocType", "Bijouterie Settings"):
        return
    
    settings = frappe.get_single("Bijouterie Settings")
    if not hasattr(settings, 'hidden_modules') or not settings.hidden_modules:
        return
    
    # Get the list of modules to hide from settings
    modules_to_hide = [d.module_name for d in settings.hidden_modules if d.module_name]
    
    if not modules_to_hide:
        return
    
    # Get current user
    user = frappe.session.user
    
    # Skip for Administrator
    if user == "Administrator":
        return
    
    # Hide specified modules for the current user
    for module in modules_to_hide:
        if frappe.db.exists("Module Def", module):
            if not frappe.db.exists("Block Module", {"parent": user, "module": module}):
                block = frappe.new_doc("Block Module")
                block.parent = user
                block.parentfield = "block_modules"
                block.parenttype = "User"
                block.module = module
                block.insert()
