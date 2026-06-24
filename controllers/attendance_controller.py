# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request


class HrisAttendanceController(http.Controller):
    """Scaffolding controller untuk endpoint Attendance sesuai API_CONTRACT.

    Catatan: placeholder (belum implementasi bisnis lengkap) agar struktur backend siap.
    """

    @http.route('/api/v1/attendance/me', type='json', auth='none', methods=['GET'], csrf=False)
    def attendance_me(self, **kwargs):
        return {
            'success': False,
            'message': 'Not implemented',
            'errors': [],
        }

    @http.route('/api/v1/attendance', type='json', auth='none', methods=['GET'], csrf=False)
    def attendance_list(self, **kwargs):
        return {
            'success': False,
            'message': 'Not implemented',
            'errors': [],
        }

    @http.route('/api/v1/attendance/correction', type='json', auth='none', methods=['POST'], csrf=False)
    def attendance_correction(self, **kwargs):
        return {
            'success': False,
            'message': 'Not implemented',
            'errors': [],
        }

