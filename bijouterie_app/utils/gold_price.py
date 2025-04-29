import frappe
from frappe.utils import today, compare

@frappe.whitelist()
def calculate_item_price(item_code, gold_weight):
    """Calcule le prix d'un article en fonction du poids d'or et du cours actuel"""
    # Récupérer le cours de l'or le plus récent
    gold_price = frappe.get_all(
        "Cours de l'Or",
        fields=["price_per_gram", "margin_percentage"],
        filters={"date": ["<=", today()]},
        order_by="date desc",
        limit=1
    )
    
    if not gold_price:
        frappe.throw("Aucun cours de l'or n'est défini. Veuillez définir le cours de l'or.")
    
    # Calculer le prix
    price_per_gram = gold_price[0].price_per_gram
    margin_percentage = gold_price[0].margin_percentage
    
    base_price = float(gold_weight) * float(price_per_gram)
    margin = base_price * (float(margin_percentage) / 100)
    final_price = base_price + margin
    
    return final_price

@frappe.whitelist()
def update_all_gold_prices():
    """Met à jour les prix de tous les articles en or"""
    # Récupérer tous les articles avec un poids d'or défini
    items = frappe.get_all(
        "Item",
        fields=["name", "gold_weight"],
        filters={"gold_weight": [">", 0]}
    )
    
    updated_count = 0
    for item in items:
        if item.gold_weight:
            new_price = calculate_item_price(item.name, item.gold_weight)
            
            # Mettre à jour le prix standard
            item_doc = frappe.get_doc("Item", item.name)
            item_doc.standard_rate = new_price
            item_doc.save()
            
            # Mettre à jour la liste de prix
            price_lists = frappe.get_all("Item Price", 
                filters={"item_code": item.name},
                fields=["name", "price_list"]
            )
            
            for pl in price_lists:
                price_list_doc = frappe.get_doc("Item Price", pl.name)
                price_list_doc.price_list_rate = new_price
                price_list_doc.save()
            
            updated_count += 1
    
    return {"status": "success", "updated_count": updated_count}
