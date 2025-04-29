import frappe
from frappe.model.document import Document

class ReparationBijou(Document):
    def on_submit(self):
        if self.status == "Livré" and not self.sales_invoice:
            self.create_sales_invoice()
    
    def create_sales_invoice(self):
        """Crée une facture pour la réparation"""
        # Calculer le coût de l'or ajouté si nécessaire
        additional_gold_cost = 0
        if self.additional_gold_weight > 0:
            gold_price = frappe.get_all(
                "Cours de l'Or",
                fields=["price_per_gram", "margin_percentage"],
                filters={},
                order_by="date desc",
                limit=1
            )
            
            if gold_price:
                price_per_gram = gold_price[0].price_per_gram
                margin_percentage = gold_price[0].margin_percentage
                
                base_price = float(self.additional_gold_weight) * float(price_per_gram)
                margin = base_price * (float(margin_percentage) / 100)
                additional_gold_cost = base_price + margin
        
        # Créer la facture
        invoice = frappe.new_doc("Sales Invoice")
        invoice.customer = self.customer
        invoice.due_date = self.delivery_date or frappe.utils.today()
        
        # Ajouter l'article de service de réparation
        invoice.append("items", {
            "item_code": "SERVICE-REPAIR-001",  # Créez cet article au préalable
            "item_name": f"Réparation - {self.repair_type}",
            "description": self.repair_details,
            "qty": 1,
            "rate": self.estimated_cost - additional_gold_cost if additional_gold_cost > 0 else self.estimated_cost
        })
        
        # Ajouter l'or supplémentaire si nécessaire
        if additional_gold_cost > 0:
            invoice.append("items", {
                "item_code": "GOLD-18K-001",  # Créez cet article au préalable
                "item_name": "Or 18 carats",
                "description": f"Or 18 carats ajouté: {self.additional_gold_weight}g",
                "qty": self.additional_gold_weight,
                "rate": additional_gold_cost / self.additional_gold_weight
            })
        
        invoice.insert()
        invoice.submit()
        
        # Mettre à jour la référence de la facture
        self.sales_invoice = invoice.name
        self.save()
        
        frappe.msgprint(f"Facture {invoice.name} créée avec succès")
        
    def validate(self):
        # Vérifier que la date de livraison promise est postérieure à la date de réception
        if self.promised_date < self.reception_date:
            frappe.throw("La date de livraison promise doit être postérieure à la date de réception")
            
        # Si le statut est "Livré", s'assurer qu'une date de livraison réelle est spécifiée
        if self.status == "Livré" and not self.delivery_date:
            self.delivery_date = frappe.utils.today()
