from frappe import _

def get_data():
	return [
		{
			"label": _("Bijouterie Operations"),
			"items": [
				{
					"type": "doctype",
					"name": "Achat Or Usage",
					"description": _("Gold Purchase Operations"),
					"onboard": 1,
				},
				{
					"type": "doctype",
					"name": "Reparation Bijou",
					"description": _("Jewelry Repair Operations"),
					"onboard": 1,
				},
				{
					"type": "doctype",
					"name": "Cours De Lor",
					"description": _("Gold Price Management"),
					"onboard": 1,
				},
			]
		},
		{
			"label": _("Settings"),
			"items": [
				{
					"type": "doctype",
					"name": "Bijouterie Settings",
					"description": _("Bijouterie App Settings"),
					"onboard": 1,
				},
			]
		}
	]
