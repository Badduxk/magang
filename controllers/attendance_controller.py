# -*- coding: utf-8 -*-
import json
import logging

# pyrefly: ignore [missing-import]
from odoo import http
# pyrefly: ignore [missing-import]
from odoo.http import request, Response

_logger = logging.getLogger(__name__)

# -------------------------------------------------------------------
# API Token for machine authentication
# In production, store this in ir.config_parameter or a secrets vault.
# -------------------------------------------------------------------
API_TOKEN_PARAM_KEY = 'hris.fingerprint_api_token'
DEFAULT_API_TOKEN = 'hris-fingerprint-secret-token-change-me'


class AttendanceController(http.Controller):
    """
    HTTP Controller for fingerprint machine integration.
    Responsibilities:
      - Define routes / endpoints
      - Validate incoming HTTP requests and authentication tokens
      - Delegate all business logic to the service layer
      - Format and return HTTP responses
    """

    # ==================================================================
    # Routes
    # ==================================================================

    @http.route(
        '/api/v1/fingerprint/push',
        type='json',
        auth='none',
        methods=['POST'],
        csrf=False,
    )
    def fingerprint_push(self, **kwargs):
        """
        Bulk fingerprint log push endpoint.

        Expected JSON payload:
        {
            "token": "your-api-token",
            "logs": [
                {
                    "machine_id": "FP-001",
                    "pin_karyawan": "12345",
                    "timestamp_mesin": "2026-06-24 08:05:00",
                    "log_type": "in"
                },
                ...
            ]
        }

        Returns:
            JSON response with processing summary.
        """
        # --- 1. Extract payload ---
        payload = request.jsonrequest
        if not payload:
            return self._error_response(
                'EMPTY_PAYLOAD',
                'Request body is empty or not valid JSON.',
                400,
            )

        # --- 2. Authenticate token ---
        token = payload.get('token', '')
        if not self._validate_token(token):
            _logger.warning('Fingerprint push: invalid API token attempt.')
            return self._error_response(
                'UNAUTHORIZED',
                'Invalid or missing API token.',
                401,
            )

        # --- 3. Validate payload structure ---
        logs = payload.get('logs', [])
        if not isinstance(logs, list) or not logs:
            return self._error_response(
                'INVALID_PAYLOAD',
                'Payload must contain a non-empty "logs" array.',
                400,
            )

        # --- 4. Delegate to service layer ---
        try:
            service = request.env['hris.attendance.service'].sudo()
            result = service.process_bulk_fingerprint_logs(logs)
        except Exception as e:
            _logger.error(
                'Fingerprint push processing error: %s', str(e), exc_info=True,
            )
            return self._error_response(
                'PROCESSING_ERROR',
                f'An error occurred during processing: {str(e)}',
                500,
            )

        # --- 5. Return success response ---
        return {
            'status': 'success',
            'message': 'Fingerprint logs processed successfully.',
            'data': result,
        }

    @http.route(
        '/api/v1/fingerprint/health',
        type='json',
        auth='none',
        methods=['GET', 'POST'],
        csrf=False,
    )
    def fingerprint_health(self, **kwargs):
        """Health check endpoint for monitoring machine connectivity."""
        return {
            'status': 'ok',
            'service': 'hris_fingerprint_sync',
            'version': '1.0.0',
        }

    # ==================================================================
    # Private helpers
    # ==================================================================

    def _validate_token(self, token):
        """
        Validate the API token against the configured system parameter.
        Falls back to DEFAULT_API_TOKEN if no parameter is set.
        """
        if not token:
            return False

        expected_token = (
            request.env['ir.config_parameter']
            .sudo()
            .get_param(API_TOKEN_PARAM_KEY, default=DEFAULT_API_TOKEN)
        )
        return token == expected_token

    @staticmethod
    def _error_response(code, message, http_status=400):
        """Build a standardized error response dict."""
        return {
            'status': 'error',
            'error': {
                'code': code,
                'message': message,
            },
        }
