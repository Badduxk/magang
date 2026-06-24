# -*- coding: utf-8 -*-
import logging

import requests

from odoo import models, api, _

_logger = logging.getLogger(__name__)

# -------------------------------------------------------------------
# Configuration — should be moved to ir.config_parameter or
# res.config.settings for production deployments.
# -------------------------------------------------------------------
WA_GATEWAY_URL = 'https://api.whatsapp-gateway.example.com/send-message'
WA_GATEWAY_API_KEY = 'YOUR_WA_GATEWAY_API_KEY'
WA_ADMIN_NUMBERS = ['628123456789']  # Target admin/leader numbers
WA_REQUEST_TIMEOUT = 5  # seconds


class WhatsAppService(models.AbstractModel):
    """
    Service layer for real-time WhatsApp notifications.
    Sends attendance event messages to corporate leaders/admins
    via an external WhatsApp Gateway API.

    Design decisions:
      - All external HTTP calls use a strict timeout to avoid blocking.
      - Failures are caught and logged — they must never crash the
        core attendance transaction.
    """
    _name = 'hris.whatsapp.service'
    _description = 'WhatsApp Notification Service'

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @api.model
    def trigger_attendance_notification(self, employee, timestamp, log_type):
        """
        Send a WhatsApp notification about an attendance event.

        Args:
            employee: hr.employee recordset (single record).
            timestamp: datetime of the attendance event.
            log_type: 'in' or 'out'.
        """
        try:
            message = self._build_attendance_message(employee, timestamp, log_type)
            self._send_whatsapp_messages(message)
        except Exception as e:
            # CRITICAL: never let WA failures propagate to the caller.
            # The attendance transaction must always succeed.
            _logger.error(
                'WhatsApp notification failed for employee %s (ID=%s): %s',
                employee.name, employee.id, str(e),
                exc_info=True,
            )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _build_attendance_message(self, employee, timestamp, log_type):
        """
        Construct a professional corporate notification message.

        Dynamically fetches:
          - Employee Name
          - Job Position (from job_id.name)
          - Formatted Timestamp
          - Status label (MASUK / PULANG)
        """
        status_label = 'MASUK' if log_type == 'in' else 'PULANG'
        status_emoji = '🟢' if log_type == 'in' else '🔴'
        job_position = employee.job_id.name if employee.job_id else '-'

        # Format timestamp for Indonesian locale
        formatted_time = timestamp.strftime('%H:%M:%S')
        formatted_date = timestamp.strftime('%d-%m-%Y')

        message = (
            f'━━━━━━━━━━━━━━━━━━━━━\n'
            f'{status_emoji} *NOTIFIKASI KEHADIRAN*\n'
            f'━━━━━━━━━━━━━━━━━━━━━\n'
            f'\n'
            f'👤 *Nama*     : {employee.name}\n'
            f'💼 *Jabatan*  : {job_position}\n'
            f'📅 *Tanggal*  : {formatted_date}\n'
            f'⏰ *Waktu*    : {formatted_time}\n'
            f'📌 *Status*   : *{status_label}*\n'
            f'\n'
            f'━━━━━━━━━━━━━━━━━━━━━\n'
            f'_Pesan otomatis dari sistem HRIS_'
        )
        return message

    def _send_whatsapp_messages(self, message):
        """
        Send the message to all configured admin WhatsApp numbers
        via the external gateway API.
        """
        # Attempt to read gateway config from system parameters (fallback to constants)
        ICP = self.env['ir.config_parameter'].sudo()
        gateway_url = ICP.get_param('hris.wa_gateway_url', default=WA_GATEWAY_URL)
        api_key = ICP.get_param('hris.wa_gateway_api_key', default=WA_GATEWAY_API_KEY)
        admin_numbers_raw = ICP.get_param(
            'hris.wa_admin_numbers',
            default=','.join(WA_ADMIN_NUMBERS),
        )
        admin_numbers = [n.strip() for n in admin_numbers_raw.split(',') if n.strip()]

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}',
        }

        for number in admin_numbers:
            payload = {
                'phone': number,
                'message': message,
            }
            try:
                response = requests.post(
                    gateway_url,
                    json=payload,
                    headers=headers,
                    timeout=WA_REQUEST_TIMEOUT,
                )
                if response.status_code == 200:
                    _logger.info(
                        'WhatsApp message sent successfully to %s', number,
                    )
                else:
                    _logger.warning(
                        'WhatsApp gateway returned status %d for number %s: %s',
                        response.status_code, number, response.text[:200],
                    )
            except requests.exceptions.Timeout:
                _logger.warning(
                    'WhatsApp gateway timeout for number %s (limit=%ds)',
                    number, WA_REQUEST_TIMEOUT,
                )
            except requests.exceptions.ConnectionError:
                _logger.warning(
                    'WhatsApp gateway connection error for number %s', number,
                )
            except requests.exceptions.RequestException as e:
                _logger.warning(
                    'WhatsApp gateway request failed for number %s: %s',
                    number, str(e),
                )