import frappe
from frappe import _

def get_data():
	return [
		{
			"module_name": "Bijouterie App",
			"color": "gold",
			"icon": "octicon octicon-gem",
			"type": "module",
			"label": _("Bijouterie")
		}
	]
