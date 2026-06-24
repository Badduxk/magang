# -*- coding: utf-8 -*-
# pyrefly: ignore [missing-import]
from odoo import models, fields


class HrisFingerprintLog(models.Model):
    """
    Stores raw fingerprint machine logs before they are processed
    into hr.attendance records.
    Thin model — only fields, relationships, and uniqueness constraints.
    """
    _name = 'hris.fingerprint.log'
    _description = 'Fingerprint Machine Raw Log'
    _order = 'timestamp_mesin desc'

    machine_id = fields.Char(
        string='Machine ID',
        required=True,
        index=True,
        help='Identifier of the physical fingerprint machine.',
    )
    pin_karyawan = fields.Char(
        string='Employee PIN',
        required=True,
        index=True,
        help='Employee PIN registered on the fingerprint machine.',
    )
    timestamp_mesin = fields.Datetime(
        string='Machine Timestamp',
        required=True,
        help='Original timestamp recorded by the fingerprint machine.',
    )
    log_type = fields.Selection(
        selection=[
            ('in', 'Check In'),
            ('out', 'Check Out'),
        ],
        string='Log Type',
        required=True,
        help='Whether this log represents a check-in or check-out event.',
    )
    is_processed = fields.Boolean(
        string='Processed',
        default=False,
        help='Indicates whether this raw log has been converted into an attendance record.',
    )
    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        ondelete='set null',
        help='Linked employee (resolved from pin_karyawan via x_fingerprint_id).',
    )

    _sql_constraints = [
        (
            'unique_fingerprint_log',
            'UNIQUE(pin_karyawan, timestamp_mesin, log_type)',
            'Duplicate fingerprint log entry: a log with the same PIN, timestamp, '
            'and type already exists.',
        ),
    ]
