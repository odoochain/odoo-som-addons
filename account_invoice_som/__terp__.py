# -*- coding: utf-8 -*-
{
    "name": "Account invoice comer (SomEnergia)",
    "description": """Este módulo añade las siguientes funcionalidades:
    * Extiende account_invoice""",
    "version": "2.103.13",
    "author": "GISCE",
    "category": "GISCEMaster",
    "depends": [
        "account_invoice_base",
        "account_payment_extension",
        "poweremail",
        "giscedata_remeses",
    ],
    "init_xml": [],
    "demo_xml": [
        "tests/account_invoice_demo.xml",
    ],
    "update_xml": [
        "account_invoice_som_report.xml",
        "account_invoice_view.xml",
        "account_invoice_data.xml",
        "wizard/wizard_payment_order_add_invoices_view.xml",
        "security/ir.model.access.csv",
    ],
    "active": False,
    "installable": True,
}
