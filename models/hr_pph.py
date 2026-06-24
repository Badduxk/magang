# -*- coding: utf-8 -*-

from odoo import fields, models


class HrisPph21(models.Model):
    _name = 'hris.pph21'
    _description = 'HRIS PPh21 (scaffolding)'

    # Placeholder fields - full calculation logic mengikuti tahap berikutnya.
    name = fields.Char()
    employee_id = fields.Many2one('hr.employee')
    year = fields.Integer()
    amount = fields.Monetary(currency_field='currency_id')
    currency_id = fields.Many2one('res.currency')

