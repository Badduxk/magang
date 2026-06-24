# -*- coding: utf-8 -*-
<<<<<<< HEAD

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

=======
import logging

# pyrefly: ignore [missing-import]
from odoo import http
# pyrefly: ignore [missing-import]
from odoo.http import request

_logger = logging.getLogger(__name__)

# API Token parameter key (shared with attendance for consistency)
API_TOKEN_PARAM_KEY = 'hris.payroll_api_token'
DEFAULT_API_TOKEN = 'hris-payroll-secret-token-change-me'


class PayrollController(http.Controller):
    """
    HTTP Controller for payroll computation endpoints.
    Responsibilities:
      - Define routes / endpoints
      - Validate incoming HTTP requests and authentication tokens
      - Delegate all business logic to the payroll service layer
      - Format and return HTTP responses
    """

    # ==================================================================
    # Routes
    # ==================================================================

    @http.route(
        '/api/v1/payroll/calculate',
        type='json',
        auth='none',
        methods=['POST'],
        csrf=False,
    )
    def calculate_payroll(self, **kwargs):
        """
        Calculate monthly payroll for a single employee.

        Expected JSON payload:
        {
            "token": "your-api-token",
            "employee_id": 42,
            "month": 6,
            "year": 2026
        }

        Returns:
            JSON response with payroll computation summary.
        """
        payload = request.jsonrequest
        if not payload:
            return self._error_response(
                'EMPTY_PAYLOAD',
                'Request body is empty or not valid JSON.',
            )

        # --- Authenticate ---
        token = payload.get('token', '')
        if not self._validate_token(token):
            _logger.warning('Payroll calculate: invalid API token attempt.')
            return self._error_response('UNAUTHORIZED', 'Invalid or missing API token.')

        # --- Validate required fields ---
        employee_id = payload.get('employee_id')
        month = payload.get('month')
        year = payload.get('year')

        validation_errors = []
        if not employee_id or not isinstance(employee_id, int):
            validation_errors.append('"employee_id" must be a positive integer.')
        if not month or not isinstance(month, int) or month < 1 or month > 12:
            validation_errors.append('"month" must be an integer between 1 and 12.')
        if not year or not isinstance(year, int) or year < 2000:
            validation_errors.append('"year" must be an integer >= 2000.')

        if validation_errors:
            return self._error_response(
                'VALIDATION_ERROR',
                ' | '.join(validation_errors),
            )

        # --- Delegate to service ---
        try:
            service = request.env['hris.payroll.service'].sudo()
            result = service.calculate_monthly_payroll(employee_id, month, year)
        except Exception as e:
            _logger.error(
                'Payroll calculation error: %s', str(e), exc_info=True,
            )
            return self._error_response(
                'PROCESSING_ERROR',
                f'An error occurred during payroll calculation: {str(e)}',
            )

        return {
            'status': 'success',
            'message': 'Payroll calculated successfully.',
            'data': result,
        }

    @http.route(
        '/api/v1/payroll/bulk-calculate',
        type='json',
        auth='none',
        methods=['POST'],
        csrf=False,
    )
    def bulk_calculate_payroll(self, **kwargs):
        """
        Calculate monthly payroll for multiple employees.

        Expected JSON payload:
        {
            "token": "your-api-token",
            "employee_ids": [42, 43, 44],
            "month": 6,
            "year": 2026
        }

        Returns:
            JSON response with per-employee payroll results.
        """
        payload = request.jsonrequest
        if not payload:
            return self._error_response(
                'EMPTY_PAYLOAD',
                'Request body is empty or not valid JSON.',
            )

        # --- Authenticate ---
        token = payload.get('token', '')
        if not self._validate_token(token):
            return self._error_response('UNAUTHORIZED', 'Invalid or missing API token.')

        # --- Validate ---
        employee_ids = payload.get('employee_ids', [])
        month = payload.get('month')
        year = payload.get('year')

        if not isinstance(employee_ids, list) or not employee_ids:
            return self._error_response(
                'VALIDATION_ERROR',
                '"employee_ids" must be a non-empty list of integers.',
            )

        if not month or not isinstance(month, int) or month < 1 or month > 12:
            return self._error_response(
                'VALIDATION_ERROR', '"month" must be between 1 and 12.',
            )
        if not year or not isinstance(year, int) or year < 2000:
            return self._error_response(
                'VALIDATION_ERROR', '"year" must be >= 2000.',
            )

        # --- Process each employee ---
        service = request.env['hris.payroll.service'].sudo()
        results = []
        errors = []

        for emp_id in employee_ids:
            try:
                result = service.calculate_monthly_payroll(emp_id, month, year)
                results.append(result)
            except Exception as e:
                _logger.error(
                    'Bulk payroll error for employee %d: %s', emp_id, str(e),
                )
                errors.append({'employee_id': emp_id, 'error': str(e)})

        return {
            'status': 'success',
            'message': f'Processed {len(results)} of {len(employee_ids)} employees.',
            'data': {
                'results': results,
                'errors': errors,
            },
        }

    # ==================================================================
    # Private helpers
    # ==================================================================

    def _validate_token(self, token):
        """Validate the API token against the configured system parameter."""
        if not token:
            return False
        expected_token = (
            request.env['ir.config_parameter']
            .sudo()
            .get_param(API_TOKEN_PARAM_KEY, default=DEFAULT_API_TOKEN)
        )
        return token == expected_token

    @staticmethod
    def _error_response(code, message):
        """Build a standardized error response dict."""
        return {
            'status': 'error',
            'error': {
                'code': code,
                'message': message,
            },
        }
>>>>>>> b86b2d617809ec4af00d64846d68a94259ce2543
