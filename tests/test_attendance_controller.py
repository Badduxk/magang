# -*- coding: utf-8 -*-
import json
# pyrefly: ignore [missing-import]
from odoo.tests.common import HttpCase, tagged

@tagged('at_install', 'post_install')
class TestAttendanceController(HttpCase):

    def test_api_push_bad_request(self):
        """Menguji apakah Controller menolak jika format payload JSON salah"""
        
        # Format salah (menggunakan key 'data' bukan 'logs')
        invalid_payload = {
            "machine_id": "MESIN-01",
            "data": []
        }

        # Simulasikan nembak API Odoo dari luar
        response = self.url_open(
            '/api/v1/fingerprint/push',
            data=json.dumps(invalid_payload),
            headers={
                'Content-Type': 'application/json',
                'Authorization': 'SecretTokenMesinFingerAnda123'
            }
        )

        # Hasilnya harus mengembalikan HTTP Status 400 Bad Request
        self.assertEqual(response.status_code, 400)

    def test_api_push_unauthorized(self):
        """Menguji apakah API menolak jika token otentikasi salah"""
        
        payload = {"logs": []}

        response = self.url_open(
            '/api/v1/fingerprint/push',
            data=json.dumps(payload),
            headers={
                'Content-Type': 'application/json',
                'Authorization': 'TOKEN_SALAH_COY'
            }
        )

        # Hasilnya harus mengembalikan HTTP Status 401 Unauthorized
        self.assertEqual(response.status_code, 401)