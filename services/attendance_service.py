# -*- coding: utf-8 -*-
import logging
from datetime import datetime, time, timedelta

# pyrefly: ignore [missing-import]
from odoo import models, api, _
# pyrefly: ignore [missing-import]
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

# Configurable late threshold: 08:00 AM local time
LATE_THRESHOLD_HOUR = 8
LATE_THRESHOLD_MINUTE = 0


class AttendanceService(models.AbstractModel):
    """
    Service layer for fingerprint log processing and attendance management.
    Fat service — contains all business logic for:
      - Bulk fingerprint log ingestion with idempotency
      - Employee PIN resolution
      - Attendance record creation/update
      - Late detection
      - WhatsApp notification triggering
    """
    _name = 'hris.attendance.service'
    _description = 'Attendance Processing Service'

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @api.model
    def process_bulk_fingerprint_logs(self, logs_data):
        """
        Process an array of raw fingerprint logs from the machine.
        Each log is expected to be a dict with keys:
            - machine_id (str)
            - pin_karyawan (str)
            - timestamp_mesin (str, ISO 8601 format)
            - log_type (str, 'in' or 'out')

        Returns:
            dict: Summary of processing results.
        """
        if not logs_data or not isinstance(logs_data, list):
            raise UserError(_('Payload must be a non-empty list of fingerprint logs.'))

        results = {
            'total_received': len(logs_data),
            'created': 0,
            'skipped_duplicate': 0,
            'skipped_no_employee': 0,
            'errors': [],
        }

        for idx, log_entry in enumerate(logs_data):
            try:
                self._process_single_log(log_entry, results)
            except Exception as e:
                _logger.warning(
                    'Error processing fingerprint log at index %d: %s',
                    idx, str(e),
                )
                results['errors'].append({
                    'index': idx,
                    'pin': log_entry.get('pin_karyawan', ''),
                    'error': str(e),
                })

        _logger.info(
            'Fingerprint bulk processing complete — '
            'received: %d, created: %d, dup_skipped: %d, no_emp: %d, errors: %d',
            results['total_received'],
            results['created'],
            results['skipped_duplicate'],
            results['skipped_no_employee'],
            len(results['errors']),
        )
        return results

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _process_single_log(self, log_entry, results):
        """Process a single fingerprint log entry."""
        # --- 1. Extract & validate fields ---
        machine_id = log_entry.get('machine_id', '')
        pin = log_entry.get('pin_karyawan', '')
        timestamp_str = log_entry.get('timestamp_mesin', '')
        log_type = log_entry.get('log_type', '')

        if not all([machine_id, pin, timestamp_str, log_type]):
            raise ValidationError(
                _('Missing required fields in log entry (machine_id, pin_karyawan, '
                  'timestamp_mesin, log_type).')
            )
        if log_type not in ('in', 'out'):
            raise ValidationError(
                _('Invalid log_type "%s". Must be "in" or "out".') % log_type
            )

        timestamp = self._parse_timestamp(timestamp_str)

        # --- 2. Idempotency check ---
        if self._log_exists(pin, timestamp, log_type):
            results['skipped_duplicate'] += 1
            return

        # --- 3. Resolve employee ---
        employee = self._resolve_employee(pin)
        if not employee:
            _logger.warning('No employee found for fingerprint PIN: %s', pin)
            results['skipped_no_employee'] += 1
            return

        # --- 4. Create raw log record ---
        fingerprint_log = self.env['hris.fingerprint.log'].sudo().create({
            'machine_id': machine_id,
            'pin_karyawan': pin,
            'timestamp_mesin': timestamp,
            'log_type': log_type,
            'employee_id': employee.id,
            'is_processed': False,
        })

        # --- 5. Create / update attendance ---
        self._upsert_attendance(employee, timestamp, log_type)

        # --- 6. Mark log as processed ---
        fingerprint_log.sudo().write({'is_processed': True})
        results['created'] += 1

        # --- 7. Trigger WhatsApp notification (fire-and-forget) ---
        wa_service = self.env['hris.whatsapp.service']
        wa_service.trigger_attendance_notification(employee, timestamp, log_type)

    def _parse_timestamp(self, timestamp_str):
        """Parse ISO 8601 timestamp string to datetime object."""
        try:
            return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            try:
                return datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                raise ValidationError(
                    _('Invalid timestamp format: "%s". '
                      'Expected ISO 8601 or "YYYY-MM-DD HH:MM:SS".') % timestamp_str
                )

    def _log_exists(self, pin, timestamp, log_type):
        """Check if a raw fingerprint log already exists (idempotency guard)."""
        return bool(
            self.env['hris.fingerprint.log'].sudo().search_count([
                ('pin_karyawan', '=', pin),
                ('timestamp_mesin', '=', timestamp),
                ('log_type', '=', log_type),
            ])
        )

    def _resolve_employee(self, pin):
        """Map a fingerprint PIN to an hr.employee record."""
        return self.env['hr.employee'].sudo().search(
            [('x_fingerprint_id', '=', pin)],
            limit=1,
        )

    def _upsert_attendance(self, employee, timestamp, log_type):
        """
        Create or update an hr.attendance record:
          - log_type 'in': create new attendance for the day if none exists.
          - log_type 'out': update the latest open attendance's check_out.
        """
        # Determine the date portion
        att_date = timestamp.date() if hasattr(timestamp, 'date') else timestamp

        Attendance = self.env['hr.attendance'].sudo()

        if log_type == 'in':
            self._handle_check_in(Attendance, employee, timestamp, att_date)
        elif log_type == 'out':
            self._handle_check_out(Attendance, employee, timestamp, att_date)

    def _handle_check_in(self, Attendance, employee, timestamp, att_date):
        """Handle a check-in event."""
        # Check if an attendance already exists for this employee on this date
        day_start = datetime.combine(att_date, time.min)
        day_end = datetime.combine(att_date, time.max)

        existing = Attendance.search([
            ('employee_id', '=', employee.id),
            ('check_in', '>=', day_start),
            ('check_in', '<=', day_end),
        ], limit=1)

        if existing:
            _logger.debug(
                'Attendance already exists for employee %s on %s, skipping check-in.',
                employee.name, att_date,
            )
            return

        # Determine lateness
        check_in_time = timestamp.time() if hasattr(timestamp, 'time') else timestamp
        is_late = (
            check_in_time.hour > LATE_THRESHOLD_HOUR
            or (check_in_time.hour == LATE_THRESHOLD_HOUR
                and check_in_time.minute > LATE_THRESHOLD_MINUTE)
        )

        Attendance.create({
            'employee_id': employee.id,
            'check_in': timestamp,
            'x_is_late': is_late,
        })
        _logger.info(
            'Created attendance check-in for %s at %s (late=%s)',
            employee.name, timestamp, is_late,
        )

    def _handle_check_out(self, Attendance, employee, timestamp, att_date):
        """Handle a check-out event by updating the most recent open attendance."""
        # Find the latest attendance without a check_out for this employee
        open_attendance = Attendance.search([
            ('employee_id', '=', employee.id),
            ('check_out', '=', False),
        ], order='check_in desc', limit=1)

        if not open_attendance:
            _logger.warning(
                'No open attendance found for employee %s on %s to record check-out.',
                employee.name, att_date,
            )
            return

        open_attendance.write({'check_out': timestamp})
        _logger.info(
            'Updated attendance check-out for %s at %s',
            employee.name, timestamp,
        )
