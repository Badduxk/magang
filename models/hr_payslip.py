# -*- coding: utf-8 -*-

from odoo import fields, models


class HrisPayslip(models.Model):
    _name = 'hris.payslip'
    _description = 'HRIS Payslip (scaffolding)'

    employee_id = fields.Many2one('hr.employee', required=True)
    payroll_month = fields.Integer()
    payroll_year = fields.Integer()
    pdf_file = fields.Char()
    whatsapp_sent = fields.Boolean(default=False)
    sent_at = fields.Datetime()

