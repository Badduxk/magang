# -*- coding: utf-8 -*-

from odoo import api, fields, models


class HrisFingerprintDevice(models.Model):
    _name = 'hris.fingerprint.device'
    _description = 'HRIS Fingerprint Device'

    name = fields.Char(required=True)
    status = fields.Selection([
        ('online', 'Online'),
        ('offline', 'Offline'),
        ('maintenance', 'Maintenance'),
    ], required=True, default='offline')


class HrisFingerprintLog(models.Model):
    _name = 'hris.fingerprint.log'
    _description = 'HRIS Fingerprint Log'

    device_id = fields.Many2one('hris.fingerprint.device', required=True)
    employee_id = fields.Many2one('hr.employee')
    scan_time = fields.Datetime(required=True)
    sync_status = fields.Selection([
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    ], required=True, default='pending')

