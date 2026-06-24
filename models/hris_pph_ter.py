# -*- coding: utf-8 -*-
# pyrefly: ignore [missing-import]
from odoo import models, fields, api
# pyrefly: ignore [missing-import]
from odoo.exceptions import ValidationError


class HrisPph21TerTable(models.Model):
    """
    Lookup table for Indonesian PPh 21 TER (Tarif Efektif Rata-rata) rates.
    Thin model — only fields and basic validation constraints.
    """
    _name = 'hris.pph21.ter.table'
    _description = 'PPh 21 TER Rate Table'
    _order = 'category, gross_start'

    category = fields.Selection(
        selection=[
            ('A', 'Category A'),
            ('B', 'Category B'),
            ('C', 'Category C'),
        ],
        string='TER Category',
        required=True,
        index=True,
        help=(
            'TER Category based on PTKP status:\n'
            '  A = TK/0, TK/1\n'
            '  B = TK/2, TK/3, K/0, K/1\n'
            '  C = K/2, K/3, K/I/0, K/I/1, K/I/2, K/I/3'
        ),
    )
    gross_start = fields.Monetary(
        string='Gross Start (IDR)',
        currency_field='currency_id',
        required=True,
        help='Lower bound of the gross salary bracket (inclusive).',
    )
    gross_end = fields.Monetary(
        string='Gross End (IDR)',
        currency_field='currency_id',
        required=True,
        help='Upper bound of the gross salary bracket (inclusive). Use 0 for unlimited.',
    )
    percentage = fields.Float(
        string='Tax Rate (%)',
        digits=(5, 2),
        required=True,
        help='Effective tax rate percentage for this bracket.',
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id.id,
    )

    @api.constrains('gross_start', 'gross_end')
    def _check_gross_range(self):
        for record in self:
            if record.gross_end and record.gross_end < record.gross_start:
                raise ValidationError(
                    'Gross End must be greater than or equal to Gross Start, '
                    'or set to 0 for unlimited upper bound.'
                )

    @api.constrains('percentage')
    def _check_percentage(self):
        for record in self:
            if record.percentage < 0 or record.percentage > 100:
                raise ValidationError(
                    'Tax rate percentage must be between 0 and 100.'
                )
