# -*- coding: utf-8 -*-

# pyrefly: ignore [missing-import]
from odoo import models, fields, api
# pyrefly: ignore [missing-import]
from odoo.exceptions import ValidationError


class HrEmployee(models.Model):
    """
    Extension of hr.employee to add HRIS-specific fields.
    Thin model — only fields, relationships, and basic constraints.
    """
    _inherit = 'hr.employee'

    x_fingerprint_id = fields.Char(
        string='Fingerprint ID',
        help='Unique PIN identifier registered on the fingerprint machine.',
        copy=False,
        index=True,
    )
    x_whatsapp_number = fields.Char(
        string='WhatsApp Number',
        help='Employee WhatsApp number for notifications (e.g., 628123456789).',
    )
    x_tax_status = fields.Selection(
        selection=[
            ('TK/0', 'TK/0 - Tidak Kawin, Tanpa Tanggungan'),
            ('TK/1', 'TK/1 - Tidak Kawin, 1 Tanggungan'),
            ('TK/2', 'TK/2 - Tidak Kawin, 2 Tanggungan'),
            ('TK/3', 'TK/3 - Tidak Kawin, 3 Tanggungan'),
            ('K/0', 'K/0 - Kawin, Tanpa Tanggungan'),
            ('K/1', 'K/1 - Kawin, 1 Tanggungan'),
            ('K/2', 'K/2 - Kawin, 2 Tanggungan'),
            ('K/3', 'K/3 - Kawin, 3 Tanggungan'),
            ('K/I/0', 'K/I/0 - Kawin, Penghasilan Istri Digabung, 0 Tanggungan'),
            ('K/I/1', 'K/I/1 - Kawin, Penghasilan Istri Digabung, 1 Tanggungan'),
            ('K/I/2', 'K/I/2 - Kawin, Penghasilan Istri Digabung, 2 Tanggungan'),
            ('K/I/3', 'K/I/3 - Kawin, Penghasilan Istri Digabung, 3 Tanggungan'),
        ],
        string='Tax Status (PTKP)',
        default='TK/0',
        help='Indonesian tax status used for PPh 21 TER category mapping.',
    )

    _sql_constraints = [
        (
            'unique_fingerprint_id',
            'UNIQUE(x_fingerprint_id)',
            'Fingerprint ID must be unique per employee.',
        ),
    ]
