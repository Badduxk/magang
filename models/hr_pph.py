# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class HrisPph21TerTable(models.Model):
    """
    Lookup table for Indonesian PPh 21 TER (Tarif Efektif Rata-rata) rates.
    This is the master data used to calculate tax based on gross income brackets.
    """
    _name = 'hris.pph21.ter.table'
    _description = 'PPh 21 TER Rate Table'
    _order = 'category, gross_start asc'

    name = fields.Char(
        string='Name',
        compute='_compute_name',
        store=True,
        help='Auto-generated description of the bracket.'
    )
    
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
        help='Upper bound of the gross salary bracket. Use 0 or a very high number for unlimited.',
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

    @api.depends('category', 'gross_start', 'gross_end')
    def _compute_name(self):
        for record in self:
            end_val = f"{record.gross_end:,.0f}" if record.gross_end > 0 else "Unlimited"
            record.name = f"Cat {record.category}: {record.gross_start:,.0f} - {end_val}"

    @api.constrains('gross_start', 'gross_end')
    def _check_gross_range(self):
        for record in self:
            # Allow gross_end to be 0 if it signifies "unlimited", otherwise check logic
            if record.gross_end != 0 and record.gross_end < record.gross_start:
                raise ValidationError(
                    'Gross End must be greater than or equal to Gross Start.'
                )

    @api.constrains('percentage')
    def _check_percentage(self):
        for record in self:
            if record.percentage < 0 or record.percentage > 100:
                raise ValidationError(
                    'Tax rate percentage must be between 0 and 100.'
                )


class HrisPph21(models.Model):
    """
    Stores the calculated PPh 21 tax records for employees.
    Links back to the employee and the period.
    """
    _name = 'hris.pph21'
    _description = 'HRIS PPh 21 Record'
    _order = 'year desc, month desc, employee_id'

    name = fields.Char(
        string='Reference',
        copy=False,
        default=lambda self: _('New')
    )
    
    employee_id = fields.Many2one(
        'hr.employee', 
        string='Employee', 
        required=True,
        index=True
    )
    
    company_id = fields.Many2one(
        'res.company', 
        string='Company', 
        required=True, 
        default=lambda self: self.env.company
    )
    
    currency_id = fields.Many2one(
        'res.currency', 
        string='Currency', 
        related='company_id.currency_id',
        store=True
    )

    # Period Information
    year = fields.Integer(string='Year', required=True, index=True)
    month = fields.Integer(string='Month', required=True, index=True)
    
    # Calculation Inputs (Snapshot)
    gross_income = fields.Monetary(
        string='Gross Income',
        currency_field='currency_id',
        help='Total gross income subject to TER calculation.'
    )
    
    ter_category = fields.Selection(
        selection=[
            ('A', 'Category A'),
            ('B', 'Category B'),
            ('C', 'Category C'),
        ],
        string='Applied TER Category',
        help='The category used for this calculation.'
    )
    
    applied_rate = fields.Float(
        string='Applied Rate (%)',
        digits=(5, 2),
        help='The percentage rate found from the TER Table.'
    )

    # Result
    amount = fields.Monetary(
        string='PPh 21 Amount',
        currency_field='currency_id',
        required=True,
        help='Final calculated tax amount.'
    )
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('paid', 'Paid'),
    ], default='draft', string='Status')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('hris.pph21') or _('New')
        return super().create(vals_list)