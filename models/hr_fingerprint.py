# -*- coding: utf-8 -*-

from odoo import api, fields, models


class HrisFingerprintDevice(models.Model):
    _name = 'hris.fingerprint.device'
    _description = 'HRIS Fingerprint Device'

    name = fields.Char(string='Device Name', required=True)
    machine_id = fields.Char(
        string='Machine ID',
        required=True,
        index=True,
        help='Unique identifier of the physical fingerprint machine.'
    )
    status = fields.Selection([
        ('online', 'Online'),
        ('offline', 'Offline'),
        ('maintenance', 'Maintenance'),
    ], string='Status', required=True, default='offline')
    
    # Relasi one2many ke log untuk memudahkan tracking
    log_ids = fields.One2many('hris.fingerprint.log', 'device_id', string='Logs')


class HrisFingerprintLog(models.Model):
    """
    Stores raw fingerprint machine logs before they are processed
    into hr.attendance records.
    """
    _name = 'hris.fingerprint.log'
    _description = 'Fingerprint Machine Raw Log'
    _order = 'timestamp_mesin desc'

    # Relasi ke Device (dari kode pertama)
    device_id = fields.Many2one(
        'hris.fingerprint.device', 
        string='Device',
        ondelete='set null',
        help='Linked fingerprint device.'
    )
    
    # Field identifikasi dari kode kedua (lebih spesifik)
    machine_id = fields.Char(
        string='Machine ID',
        required=True,
        index=True,
        help='Identifier of the physical fingerprint machine (redundant if device_id is set, but useful for raw data).'
    )
    
    pin_karyawan = fields.Char(
        string='Employee PIN',
        required=True,
        index=True,
        help='Employee PIN registered on the fingerprint machine.'
    )
    
    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        ondelete='set null',
        help='Linked employee (resolved from pin_karyawan via x_fingerprint_id).'
    )
    
    timestamp_mesin = fields.Datetime(
        string='Machine Timestamp',
        required=True,
        help='Original timestamp recorded by the fingerprint machine.'
    )
    
    # Menggabungkan konsep scan_time dan timestamp_mesin
    # Kita gunakan timestamp_mesin sebagai waktu asli mesin
    
    log_type = fields.Selection(
        selection=[
            ('in', 'Check In'),
            ('out', 'Check Out'),
        ],
        string='Log Type',
        required=True,
        help='Whether this log represents a check-in or check-out event.'
    )
    
    # Menggabungkan konsep sync_status dan is_processed
    sync_status = fields.Selection([
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    ], string='Sync Status', required=True, default='pending', help='Status of synchronization with attendance system.')
    
    is_processed = fields.Boolean(
        string='Processed',
        default=False,
        help='Indicates whether this raw log has been converted into an attendance record.'
    )

    _sql_constraints = [
        (
            'unique_fingerprint_log',
            'UNIQUE(pin_karyawan, timestamp_mesin, log_type)',
            'Duplicate fingerprint log entry: a log with the same PIN, timestamp, '
            'and type already exists.',
        ),
    ]