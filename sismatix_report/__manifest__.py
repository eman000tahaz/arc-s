# -*- coding: utf-8 -*-
{
    'name': 'Sismatix Report',
    'version': '1.0.1',
    'Author': "Eman Taha",
    'category': 'Other',
    'sequence': 20,
    'summary': 'Sismatix Report',
    'depends': ['web'],
    'data': [
        'security/sismatix_security.xml',
        'views/ir_model_fields_view.xml',
        'views/sismatix_report.xml',
        'report/report_sismatix.xml',
        'wizard/change_tree_fields_view.xml',
        'views/sismatix_report_assets.xml',
    ],
    'demo': [
    ],
    'qweb': [
        "static/src/xml/web_print_view_template.xml",
        "static/src/xml/web_export_view_template.xml",
    ],
    'installable': True,
    'application': True,
}
