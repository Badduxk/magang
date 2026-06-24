# -*- coding: utf-8 -*-

from odoo import api, fields, models


class HrisPayslip(models.Model):
    """
    Custom HRIS Payslip model combining payroll computation and distribution tracking.
    Thin model — focuses on fields and relationships for Community Edition.
    """
    _name = 'hris.payslip'
    _description = 'HRIS Custom Payslip'
    _order = 'date_from desc'

    # --- Basic Information & Relations ---
    name = fields.Char(
        string='Reference', 
        required=True, 
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

    # --- Period Definition ---
    # Menggabungkan konsep payroll_month/year dengan date range yang lebih fleksibel
    date_from = fields.Date(string='From Date', required=True)
    date_to = fields.Date(string='To Date', required=True)
    
    payroll_month = fields.Integer(
        string='Payroll Month',
        compute='_compute_payroll_period',
        store=True,
        help='Month extracted from date_from.'
    )
    payroll_year = fields.Integer(
        string='Payroll Year',
        compute='_compute_payroll_period',
        store=True,
        help='Year extracted from date_from.'
    )

    # --- Financial Components (From Code 2) ---
    x_gross_salary = fields.Monetary(
        string='Gross Salary',
        currency_field='currency_id',
        help='Total gross salary before any deductions.',
    )
    x_pph21_amount = fields.Monetary(
        string='PPh 21 Amount',
        currency_field='currency_id',
        help='Income tax deduction computed using TER method.',
    )
    x_bpjs_deduction = fields.Monetary(
        string='BPJS Deduction',
        currency_field='currency_id',
        help='Total BPJS contribution (Kesehatan + Ketenagakerjaan employee portion).',
    )
    x_late_deduction = fields.Monetary(
        string='Late Deduction',
        currency_field='currency_id',
        help='Penalty deduction for late arrivals during the pay period.',
    )
    x_net_salary = fields.Monetary(
        string='Net Salary (THP)',
        currency_field='currency_id',
        help='Take Home Pay = Gross - Late Deduction - BPJS - PPh 21.',
    )

    # --- Distribution & Tracking (From Code 1) ---
    pdf_file = fields.Char(
        string='PDF Attachment Path',
        help='Path or attachment ID for the generated payslip PDF.'
    )
    whatsapp_sent = fields.Boolean(
        string='WhatsApp Sent', 
        default=False,
        help='Indicates if the payslip has been sent via WhatsApp.'
    )
    sent_at = fields.Datetime(
        string='Sent At',
        help='Timestamp when the payslip was distributed.'
    )

    @api.depends('date_from')
    def _compute_payroll_period(self):
        """Extract month and year from date_from for easier reporting."""
        for record in self:
            if record.date_from:
                record.payroll_month = record.date_from.month
                record.payroll_year = record.date_from.year
            else:
                record.payroll_month = False
                record.payroll_year = False

    @api.model_create_multi
    def create(self, vals_list):
        """Auto-generate reference name if not provided."""
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('hris.payslip') or _('New')
        return super().create(vals_list)