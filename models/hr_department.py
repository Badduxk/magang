# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class HrDepartment(models.Model):
    _inherit = 'hr.department'

    department_code = fields.Char(string='Department Code', required=True, index=True, copy=False)

    _sql_constraints = [
        ('uniq_department_code', 'unique(department_code)', 'Department code must be unique.'),
    ]

    @api.constrains('department_code')
    def _check_department_code_format(self):
        for rec in self:
            if rec.department_code and not rec.department_code.startswith('DEPT-'):
                raise ValidationError(_('department_code format must be DEPT-XX'))

