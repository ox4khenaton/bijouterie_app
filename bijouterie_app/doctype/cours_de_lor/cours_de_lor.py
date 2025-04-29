import frappe
from frappe.model.document import Document

class CoursdelOr(Document):
    def after_insert(self):
        """Après l'insertion d'un nouveau cours de l'or, proposer de mettre à jour tous les prix"""
        frappe.msgprint(
            "Nouveau cours de l'or enregistré. Voulez-vous mettre à jour les prix de tous les articles en or?",
            title="Mise à jour des prix",
            primary_action={
                'label': 'Mettre à jour maintenant',
                'server_action': 'bijouterie_app.bijouterie_app.utils.gold_price.update_all_gold_prices'
            }
        )
    
    def validate(self):
        """Valider les données du cours de l'or"""
        # Vérifier que le prix par gramme est positif
        if self.price_per_gram <= 0:
            frappe.throw("Le prix par gramme doit être supérieur à zéro.")
        
        # Vérifier que la marge est positive
        if self.margin_percentage < 0:
            frappe.throw("La marge ne peut pas être négative.")
