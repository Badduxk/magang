# -*- coding: utf-8 -*-
{
    'name': 'HRIS Core',
    'version': '1.0.0',
    'category': 'Human Resources',
    'summary': 'HRIS base module (Employee extensions)',
'depends': ['hr', 'hris_base'],
    'data': [


        'security/hris_employee_security.xml',
        'security/ir.model.access.csv',
        'views/hr_employee_views.xml',

        'views/hr_department_views.xml',
        'views/hr_work_location_views.xml',
        'data/ir_sequence_data.xml',
        'menu.xml',
    ],
    'external_dependencies': {},
    'assets': {},
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}


