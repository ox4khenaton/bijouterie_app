import frappe
from frappe.model.document import Document

class AchatOrUsage(Document):
    def validate(self):
        self.calculate_totals()
    
    def calculate_totals(self):
        """Calcule les totaux pour le poids et le montant"""
        total_weight = 0
        total_amount = 0
        
        for item in self.gold_items:
            total_weight += item.weight
            total_amount += item.amount
        
        self.total_weight = total_weight
        self.total_amount = total_amount

    def on_submit(self):
        """Après la soumission, proposer de créer une entrée de stock"""
        frappe.msgprint(
            "Achat d'or usagé enregistré. Voulez-vous créer une entrée de stock?",
            title="Création d'entrée de stock",
            primary_action={
                'label': 'Créer maintenant',
                'server_action': 'bijouterie_app.bijouterie_app.doctype.achat_or_usage.achat_or_usage.create_stock_entry',
                'args': {'doc_name': self.name}
            }
        )

@frappe.whitelist()
def create_stock_entry(doc_name):
    """Crée une entrée de stock pour l'or usagé acheté"""
    purchase_doc = frappe.get_doc("Achat Or Usagé", doc_name)
    
    if not purchase_doc.docstatus == 1:
        frappe.throw("Le document doit être soumis avant de créer une entrée de stock")
    
    # Créer l'entrée de stock
    stock_entry = frappe.new_doc("Stock Entry")
    stock_entry.stock_entry_type = "Material Receipt"
    stock_entry.to_warehouse = frappe.db.get_single_value("Bijouterie Settings", "default_gold_warehouse") or "Stores - B"
    stock_entry.posting_date = purchase_doc.purchase_date
    
    # Regrouper par carats
    carat_groups = {}
    for item in purchase_doc.gold_items:
        carat = item.gold_carat
        if carat not in carat_groups:
            carat_groups[carat] = 0
        carat_groups[carat] += item.weight
    
    # Ajouter les articles à l'entrée de stock
    for carat, weight in carat_groups.items():
        # Trouver ou créer l'article d'or correspondant
        item_code = f"OR-USAGE-{carat}K"
        if not frappe.db.exists("Item", item_code):
            create_gold_item(item_code, carat)
        
        # Ajouter à l'entrée de stock
        stock_entry.append("items", {
            "item_code": item_code,
            "qty": weight,
            "basic_rate": purchase_doc.total_amount / purchase_doc.total_weight,
            "description": f"Or usagé {carat}K acheté le {purchase_doc.purchase_date}",
            "reference_doctype": "Achat Or Usagé",
            "reference_docname": purchase_doc.name
        })
    
    stock_entry.insert()
    stock_entry.submit()
    
    return stock_entry.name

def create_gold_item(item_code, carat):
    """Crée un nouvel article pour l'or usagé"""
    item = frappe.new_doc("Item")
    item.item_code = item_code
    item.item_name = f"Or usagé {carat}K"
    item.item_group = "Matières premières"
    item.stock_uom = "Gram"
    item.is_stock_item = 1
    item.include_item_in_manufacturing = 1
    item.gold_carat = carat
    item.description = f"Or usagé {carat} carats pour recyclage"
    item.insert()
    
    return item.name
