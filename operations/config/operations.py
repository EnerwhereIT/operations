from __future__ import unicode_literals
from frappe import _

def get_data():
    return [
        # data
        {
            "label": _("Operations"),
            "items": [
                {
                    "type": "doctype",
                    "name": "Plants",
                    "onboard": 1,
                },
                {
                    "type": "doctype",
                    "name": "Diesel Price",
                    "onboard": 1
                },
                {
                    "type": "doctype",
                    "name": "Meter Reading",
                    "onboard": 1
                }
            ]
        }
    ]