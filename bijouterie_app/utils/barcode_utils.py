import frappe
import random
import string
import barcode
from barcode.writer import ImageWriter
from io import BytesIO
import base64
from frappe.model.document import Document
import json
from frappe.utils import get_files_path

def generate_barcode_number(item_doc):
    """Génère un numéro de code-barres unique pour un article de bijouterie"""
    # Format: BIJ-[Type de bijou (2 lettres)]-[Poids en g (3 chiffres)]-[Numéro aléatoire (4 chiffres)]
    
    # Déterminer le préfixe selon le type de bijou
    jewelry_type_map = {
        "Bague": "BA",
        "Bracelet": "BR",
        "Collier": "CO",
        "Boucles d'oreilles": "BO",
        "Pendentif": "PE",
        "Montre": "MO",
        "Autre": "AU"
    }
    
    jewelry_type = item_doc.get("jewelry_type", "Autre")
    type_prefix = jewelry_type_map.get(jewelry_type, "AU")
    
    # Formater le poids (3 chiffres, avec zéros devant si nécessaire)
    weight = item_doc.get("gold_weight", 0)
    weight_str = f"{int(weight * 10):03d}"  # Multiplié par 10 pour inclure 1 décimale
    
    # Générer un numéro aléatoire à 4 chiffres
    random_num = ''.join(random.choices(string.digits, k=4))
    
    # Assembler le code-barres
    barcode_number = f"BIJ-{type_prefix}-{weight_str}-{random_num}"
    
    # Vérifier l'unicité
    existing_items = frappe.get_all("Item", filters={"barcode_bijouterie": barcode_number})
    while existing_items:
        random_num = ''.join(random.choices(string.digits, k=4))
        barcode_number = f"BIJ-{type_prefix}-{weight_str}-{random_num}"
        existing_items = frappe.get_all("Item", filters={"barcode_bijouterie": barcode_number})
    
    return barcode_number

@frappe.whitelist()
def generate_item_barcode(item_code):
    """Génère un code-barres pour un article spécifique"""
    item_doc = frappe.get_doc("Item", item_code)
    
    # Vérifier si l'article a déjà un code-barres
    if item_doc.get("barcode_bijouterie"):
        return {"status": "exists", "barcode": item_doc.barcode_bijouterie}
    
    # Générer un nouveau numéro de code-barres
    barcode_number = generate_barcode_number(item_doc)
    
    # Créer l'image du code-barres
    code128 = barcode.get('code128', barcode_number, writer=ImageWriter())
    buffer = BytesIO()
    code128.write(buffer)
    
    # Convertir l'image en base64
    buffer.seek(0)
    barcode_image_b64 = base64.b64encode(buffer.getvalue()).decode()
    
    # Sauvegarder l'image comme fichier
    filename = f"barcode_{barcode_number}.png"
    _file = frappe.get_doc({
        "doctype": "File",
        "file_name": filename,
        "content": barcode_image_b64,
        "is_private": 0
    })
    _file.insert()
    
    # Mettre à jour l'article avec le code-barres
    item_doc.barcode_bijouterie = barcode_number
    item_doc.barcode_image = _file.file_url
    item_doc.save()
    
    return {
        "status": "success", 
        "barcode": barcode_number, 
        "image_url": _file.file_url
    }

@frappe.whitelist()
def generate_all_barcodes():
    """Génère des codes-barres pour tous les articles de bijouterie sans code-barres"""
    # Récupérer tous les articles de bijouterie sans code-barres
    items = frappe.get_all(
        "Item",
        fields=["name"],
        filters=[
            ["gold_weight", ">", 0],
            ["barcode_bijouterie", "=", ""]
        ]
    )
    
    generated_count = 0
    for item in items:
        result = generate_item_barcode(item.name)
        if result.get("status") == "success":
            generated_count += 1
    
    return {"status": "success", "generated_count": generated_count}

@frappe.whitelist()
def get_barcode_print_html(item_code):
    """Génère le HTML pour l'impression du code-barres d'un article"""
    item_doc = frappe.get_doc("Item", item_code)
    
    if not item_doc.get("barcode_bijouterie") or not item_doc.get("barcode_image"):
        # Générer le code-barres s'il n'existe pas
        result = generate_item_barcode(item_code)
        if result.get("status") != "success":
            frappe.throw("Impossible de générer le code-barres pour cet article.")
        
        # Recharger l'article avec le nouveau code-barres
        item_doc = frappe.get_doc("Item", item_code)
    
    # Construire le HTML pour l'impression
    company = frappe.defaults.get_global_default('company')
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Code-barres {item_doc.barcode_bijouterie}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 0; padding: 10mm; }}
            .barcode-container {{ text-align: center; margin-bottom: 5mm; }}
            .barcode-image {{ max-width: 100%; height: auto; }}
            .item-info {{ text-align: center; font-size: 12pt; }}
            .company-name {{ font-weight: bold; font-size: 14pt; margin-bottom: 3mm; }}
            .barcode-number {{ font-family: monospace; font-size: 12pt; margin-top: 2mm; }}
            .item-details {{ margin-top: 5mm; font-size: 10pt; }}
            @media print {{
                @page {{ size: 50mm 30mm; margin: 0; }}
                body {{ width: 50mm; height: 30mm; margin: 0; padding: 2mm; }}
            }}
        </style>
    </head>
    <body>
        <div class="barcode-container">
            <div class="company-name">{company}</div>
            <img src="{item_doc.barcode_image}" class="barcode-image">
            <div class="barcode-number">{item_doc.barcode_bijouterie}</div>
            <div class="item-details">
                {item_doc.item_name}<br>
                {item_doc.gold_weight}g - 18K
            </div>
        </div>
    </body>
    </html>
    """
    
    return html

@frappe.whitelist()
def print_all_barcodes(item_codes=None, filter_type=None):
    """Génère une page HTML pour imprimer plusieurs codes-barres à la fois"""
    items = []
    
    if item_codes:
        # Convertir la chaîne JSON en liste
        if isinstance(item_codes, str):
            item_codes = json.loads(item_codes)
        
        # Récupérer les articles spécifiés
        for item_code in item_codes:
            items.append(frappe.get_doc("Item", item_code))
    else:
        # Filtrer selon le type spécifié
        filters = [["gold_weight", ">", 0]]
        
        if filter_type == "no_barcode":
            filters.append(["barcode_bijouterie", "=", ""])
        elif filter_type == "all_gold":
            pass  # Déjà filtré par gold_weight > 0
        elif filter_type and filter_type.startswith("type_"):
            jewelry_type = filter_type[5:]  # Extraire le type après "type_"
            filters.append(["jewelry_type", "=", jewelry_type])
        
        # Récupérer les articles selon les filtres
        item_list = frappe.get_all(
            "Item",
            fields=["name"],
            filters=filters
        )
        
        for item in item_list:
            items.append(frappe.get_doc("Item", item.name))
    
    # Générer les codes-barres manquants
    for item in items:
        if not item.get("barcode_bijouterie") or not item.get("barcode_image"):
            generate_item_barcode(item.name)
    
    # Recharger les articles pour avoir les codes-barres à jour
    updated_items = []
    for item in items:
        updated_items.append(frappe.get_doc("Item", item.name))
    
    # Construire le HTML pour l'impression
    company = frappe.defaults.get_global_default('company')
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Impression des codes-barres</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; }}
            .page-container {{ display: flex; flex-wrap: wrap; }}
            .barcode-container {{ 
                width: 50mm; 
                height: 30mm; 
                text-align: center; 
                padding: 2mm; 
                box-sizing: border-box;
                page-break-inside: avoid;
            }}
            .barcode-image {{ max-width: 100%; height: auto; max-height: 15mm; }}
            .company-name {{ font-weight: bold; font-size: 8pt; margin-bottom: 1mm; }}
            .barcode-number {{ font-family: monospace; font-size: 7pt; margin-top: 1mm; }}
            .item-details {{ font-size: 7pt; margin-top: 1mm; }}
            @media print {{
                body {{ width: 210mm; height: 297mm; }} /* A4 */
                .page-break {{ page-break-after: always; }}
            }}
        </style>
    </head>
    <body>
        <div class="page-container">
    """
    
    for i, item in enumerate(updated_items):
        if not item.get("barcode_bijouterie") or not item.get("barcode_image"):
            continue
            
        html += f"""
            <div class="barcode-container">
                <div class="company-name">{company}</div>
                <img src="{item.barcode_image}" class="barcode-image">
                <div class="barcode-number">{item.barcode_bijouterie}</div>
                <div class="item-details">
                    {item.item_name}<br>
                    {item.gold_weight}g - 18K
                </div>
            </div>
        """
        
        # Ajouter un saut de page tous les 24 codes-barres (6x4 sur une page A4)
        if (i + 1) % 24 == 0 and i < len(updated_items) - 1:
            html += '<div class="page-break"></div>'
    
    html += """
        </div>
    </body>
    </html>
    """
    
    return html
