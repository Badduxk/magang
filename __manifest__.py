# -*- coding: utf-8 -*-
{
    'name': 'HRIS Backend',
    'version': '19.0.1.0.0',
    'category': 'Human Resources',
    'summary': 'HRIS Backend: Fingerprint Attendance, WhatsApp Notifications, Payroll & PPh 21 TER',
    'description': """
        Custom HRIS backend module implementing a layered architecture:
        Routes -> Controller -> Service -> Model.

        Features:
        - Fingerprint machine integration with bulk sync API
        - Automated attendance creation from fingerprint logs
        - Real-time WhatsApp notifications for attendance events
        - Payroll computation with Indonesian PPh 21 TER scheme
        - BPJS deduction calculations
        - Late penalty deductions
    """,
    'author': 'HRIS Dev Team',
    'website': '',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'hr',
        'hr_attendance',
        'hr_contract',
        # 'hris_base',  # jika modul dasar ini ada, tambahkan
    ],
    'data': [
        # Security
        'security/hris_employee_security.xml',
        'security/ir.model.access.csv',

        # Views
        'views/hr_employee_views.xml',
        'views/hr_department_views.xml',
        'views/hr_work_location_views.xml',

        # Data (sequence)
        'data/ir_sequence_data.xml',

        # Menu
        'menu.xml',
    ],
    'external_dependencies': {},
    'assets': {},
    'installable': True,
    'application': True,
    'auto_install': False,
}