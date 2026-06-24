# -*- coding: utf-8 -*-

# pyrefly: ignore [missing-import]
from odoo.tests.common import TransactionCase, tagged
# pyrefly: ignore [missing-import]
from odoo.fields import Datetime

from unittest.mock import patch

@tagged('at_install', 'post_install')
class TestAttendanceService(TransactionCase):

    def setUp(self):
        super(TestAttendanceService, self).setUp()
        
        # 1. Buat data Karyawan untuk Testing
        self.employee = self.env['hr.employee'].create({
            'name': 'Reza Backend Dev',
            'x_fingerprint_id': 'FING-99',
            'x_whatsapp_number': '628123456789'
        })
        
        # 2. Ambil instance Service Layer
        self.attendance_service = self.env['hris.attendance.service']

    @patch('odoo.addons.hris_backend.services.whatsapp_service.WhatsappService._send_via_gateway')
    def test_process_bulk_logs_success_and_idempotency(self, mock_send_wa):
        """Menguji sukses pemrosesan data bulk & pencegahan duplikasi data offline"""
        
        # Payload tiruan seolah-olah mesin finger baru online kembali
        raw_logs = [
            {"pin_karyawan": "FING-99", "timestamp_mesin": "2026-06-24 07:45:00", "log_type": "in"},
            {"pin_karyawan": "FING-99", "timestamp_mesin": "2026-06-24 07:45:00", "log_type": "in"} # Sengaja diduplikat
        ]

        # Eksekusi Service Layer
        processed, skipped = self.attendance_service.process_bulk_logs(raw_logs)

        # KONDISI 1: Log pertama harus sukses, log kedua harus di-skip karena duplikat
        self.assertEqual(processed, 1, "Harusnya hanya 1 log yang diproses.")
        self.assertEqual(skipped, 1, "Harusnya 1 log duplikat berhasil di-skip.")

        # KONDISI 2: Cek apakah record absensi sah (hr.attendance) terbentuk dengan benar
        attendance = self.env['hr.attendance'].search([('employee_id', '=', self.employee.id)], limit=1)
        self.assertTrue(attendance, "Record hr.attendance harusnya terbentuk.")
        self.assertFalse(attendance.x_is_late, "Karyawan masuk jam 07:45, tidak boleh dianggap terlambat.")

        # KONDISI 3: Pastikan fungsi kirim WA terpicu (Mock ter-call)
        self.assertTrue(mock_send_wa.called, "Fungsi WA Gateway harusnya terpicu.")

    @patch('odoo.addons.hris_backend.services.whatsapp_service.WhatsappService._send_via_gateway')
    def test_attendance_late_logic(self, mock_send_wa):
        """Menguji apakah karyawan otomatis ditandai terlambat jika lewat jam 08:00"""
        
        raw_logs = [
            {"pin_karyawan": "FING-99", "timestamp_mesin": "2026-06-24 08:30:00", "log_type": "in"}
        ]

        self.attendance_service.process_bulk_logs(raw_logs)
        attendance = self.env['hr.attendance'].search([('employee_id', '=', self.employee.id)], limit=1)

        # KONDISI: Masuk jam 08:30 wajib membuat field x_is_late menjadi True
        self.assertTrue(attendance.x_is_late, "Karyawan masuk jam 08:30 harusnya ditandai terlambat (True).")