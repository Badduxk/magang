# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class HrWorkLocation(models.Model):
    _inherit = 'hr.work.location'

    location_status = fields.Selection(
        selection=[
            ('active', 'Active'),
            ('inactive', 'Inactive'),
        ],
        string='Location Status',
        required=True,
        default='active',
    )

    address = fields.Text(string='Address', required=True)
    city = fields.Char(string='City', required=True)
    province = fields.Char(string='Province', required=True)
    postal_code = fields.Char(string='Postal Code')

    @api.constrains('address', 'city', 'province')
    def _check_required_text_fields(self):
        for rec in self:
            if not rec.address or not rec.city or not rec.province:
                raise ValidationError(_('Work location address, city, and province are required.'))

