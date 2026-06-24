# -*- coding: utf-8 -*-

from odoo import http


class HrisPayrollController(http.Controller):
    """Scaffolding controller untuk endpoint Payroll sesuai API_CONTRACT.

    Catatan: placeholder.
    """

    @http.route('/api/v1/payroll', type='json', auth='none', methods=['GET'], csrf=False)
    def payroll_list(self, **kwargs):
        return {
            'success': False,
            'message': 'Not implemented',
            'errors': [],
        }

    @http.route('/api/v1/payroll/generate', type='json', auth='none', methods=['POST'], csrf=False)
    def payroll_generate(self, **kwargs):
        return {
            'success': False,
            'message': 'Not implemented',
            'errors': [],
        }

