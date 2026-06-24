# -*- coding: utf-8 -*-
# pyrefly: ignore [missing-import]
from odoo import models, fields


class HrPayslipCustom(models.Model):
    """
    Custom HRIS payroll computation fields for Odoo Community.
    Thin model — only fields, no business logic.
    """
    _name = 'hr.payslip'
    _description = 'HRIS Custom Payslip'

    # Karena bikin tabel baru, kita wajib tambahkan fields relasi & dasar
    name = fields.Char(string='Reference', required=True, default='New')
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    date_from = fields.Date(string='From', required=True)
    date_to = fields.Date(string='To', required=True)
    
    # Field mata uang (diperlukan oleh fields.Monetary)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency', related='company_id.currency_id')

    # Fields kustom HRIS lo tetap aman di bawah ini
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