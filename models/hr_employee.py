# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

from odoo.exceptions import ValidationError


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    employee_code = fields.Char(string='Employee Code', required=True, copy=False, readonly=False)
    employee_status = fields.Selection(
        selection=[
            ('active', 'Active'),
            ('inactive', 'Inactive'),
            ('resigned', 'Resigned'),
        ],
        string='Employee Status',
        required=True,
        default='active',
    )

    join_date = fields.Date(string='Join Date', required=True)

    # NIK: use identification_id mapping.
    nik = fields.Char(string='NIK', size=16, required=True, index=True, copy=False)

    npwp_number = fields.Char(string='NPWP Number', required=True)

    employee_type = fields.Selection(
        selection=[
            ('tetap', 'Tetap'),
            ('freelance', 'Freelance'),
        ],
        string='Employee Type',
        required=True,
        default='tetap',
    )

    bank_name = fields.Char(string='Bank Name')
    bank_account_number = fields.Char(string='Bank Account Number')

    _sql_constraints = [
        ('uniq_employee_code', 'unique(employee_code)', 'Employee code must be unique.'),
        ('uniq_nik', 'unique(nik)', 'NIK must be unique.'),
    ]

    @api.model
    def create(self, vals):
        # employee_code auto sequence
        if not vals.get('employee_code'):
            vals['employee_code'] = self.env['ir.sequence'].next_by_code('hris.employee.code')

        # keep NIK/identification_id consistent
        if vals.get('nik'):
            if len(vals['nik']) != 16 or not vals['nik'].isdigit():
                raise ValidationError(_('NIK must be 16 digits.'))
            # ensure Odoo identification_id mirrors custom nik
            vals['identification_id'] = vals.get('identification_id') or vals['nik']

        # soft delete consistency
        # If Odoo active=False is set, reflect it in employee_status.
        if vals.get('active') is False:
            vals['employee_status'] = vals.get('employee_status') or 'resigned'

        return super().create(vals)

    def write(self, vals):
        # keep NIK/identification_id consistent
        if vals.get('nik'):
            if len(vals['nik']) != 16 or not vals['nik'].isdigit():
                raise ValidationError(_('NIK must be 16 digits.'))
            vals['identification_id'] = vals.get('identification_id') or vals['nik']

        # soft delete consistency (both directions)
        if 'employee_status' in vals:
            if vals['employee_status'] == 'resigned':
                vals['active'] = False
            elif vals['employee_status'] in ('active', 'inactive'):
                # leave provided active if any; otherwise default to True
                if vals.get('active') is None:
                    vals['active'] = True

        if vals.get('active') is False:
            vals['employee_status'] = vals.get('employee_status') or 'resigned'



        return super().write(vals)

    @api.constrains('nik')
    def _check_nik_format(self):
        for rec in self:

            if rec.nik and (len(rec.nik) != 16 or not rec.nik.isdigit()):
                raise ValidationError(_('NIK must be 16 digits.'))

    @api.model
    def _sync_nik_from_identification_id(self):
        for rec in self:
            if not rec.nik and rec.identification_id:
                rec.nik = rec.identification_id

    # Related helper fields for API/exports
    full_name = fields.Char(string='Full Name', related='name', store=False, readonly=True)
    email = fields.Char(string='Email', related='work_email', store=False, readonly=True)
    phone_number = fields.Char(string='Phone Number', related='mobile_phone', store=False, readonly=True)

    def _prepare_portal_export_values(self):
        self.ensure_one()
        return {
            'employee_id': self.id,
            'employee_code': self.employee_code,
            'nik': self.nik,
            'full_name': self.name,
            'email': self.work_email,
            'phone_number': self.mobile_phone,
            'employee_type': self.employee_type,
            'department': self.department_id.name if self.department_id else None,
            'job_position': self.job_id.name if self.job_id else None,
            'join_date': self.join_date,
            'status': self.employee_status,
        }


