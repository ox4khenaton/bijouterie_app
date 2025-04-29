import frappe
from frappe.utils import compare

def validate_gold_item(doc, method):
    """Valide les articles en or et applique les règles spécifiques"""
    # Vérifier si c'est un article en or (basé sur le groupe d'articles ou un champ personnalisé)
    if doc.get("gold_weight"):
        # S'assurer que le poids est positif
        if doc.gold_weight <= 0:
            frappe.throw("Le poids de l'or doit être supérieur à zéro.")
        
        # S'assurer que le titrage est à 18 carats pour les nouveaux articles
        if not doc.get("gold_carat"):
            doc.gold_carat = "18"
        elif doc.gold_carat != "18" and not doc.get("is_old_gold"):
            frappe.msgprint("Attention: Tous les nouveaux bijoux doivent être en or 18 carats selon la réglementation algérienne.")
            
        # Mettre à jour le prix en fonction du poids et du cours de l'or si nécessaire
        update_gold_price(doc)

def update_gold_price(item_doc):
    """Met à jour le prix d'un article en or en fonction de son poids et du cours actuel"""
    if not item_doc.get("gold_weight"):
        return
        
    # Récupérer le cours de l'or le plus récent
    gold_price = frappe.get_all(
        "Cours de l'Or",
        fields=["price_per_gram", "margin_percentage"],
        filters={},
        order_by="date desc",
        limit=1
    )
    
    if not gold_price:
        return  # Pas de cours d'or défini, ne pas mettre à jour le prix
    
    # Calculer le prix
    price_per_gram = gold_price[0].price_per_gram
    margin_percentage = gold_price[0].margin_percentage
    
    base_price = float(item_doc.gold_weight) * float(price_per_gram)
    margin = base_price * (float(margin_percentage) / 100)
    final_price = base_price + margin
    
    # Mettre à jour le prix standard de l'article
    if not item_doc.standard_rate or compare(abs(item_doc.standard_rate - final_price), ">", 0.01):
        item_doc.standard_rate = final_price
        frappe.msgprint(f"Prix mis à jour en fonction du cours de l'or: {final_price}")
