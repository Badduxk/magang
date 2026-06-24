# -*- coding: utf-8 -*-
# pyrefly: ignore [missing-import]
from odoo.tests.common import TransactionCase,tagged

@tagged('at_install', 'post_install')
class TestPayrollService(TransactionCase):

    def setUp(self):
        super(TestPayrollService, self).setUp()
        
        # 1. Buat Karyawan dengan Status Pajak TK/0 (Kategori TER A)
        self.employee = self.env['hr.employee'].create({
            'name': 'Reza Gaji Pokok',
            'x_tax_status': 'TK/0'
        })
        
        # 2. Buat Kontrak Kerja Tiruan (Gaji Pokok 10 Juta)
        self.contract = self.env['hr.contract'].create({
            'name': 'Kontrak Kerja Reza',
            'employee_id': self.employee.id,
            'wage': 10000000.0,
            'state': 'open'
        })
        self.employee.contract_id = self.contract.id

        # 3. Buat Aturan Tarif Pajak TER di Database untuk Kategori A
        # Misal: Pendapatan Rp 5.400.001 - Rp 10.000.000 kena tarif 2%
        self.env['hris.pph21.ter.table'].create({
            'category': 'A',
            'gross_start': 5400001,
            'gross_end': 10000000,
            'percentage': 2.0
        })
        
        self.payroll_service = self.env['hris.payroll.service']

    def test_calculate_pph21_ter_matching(self):
        """Memastikan pencarian dan kalkulasi tarif TER PPh 21 presisi"""
        gross_salary = 10000000.0 # 10 Juta
        
        # Jalankan fungsi hitung pajak internal di Service
        calculated_tax = self.payroll_service._calculate_pph21_ter(self.employee, gross_salary)
        
        # Ekspektasi: 2% dari 10.000.000 = 200.000
        self.assertEqual(calculated_tax, 200000.0, "Kalkulasi TER PPh 21 salah hitung!")

    def test_full_payroll_generation(self):
        """Memastikan data slip gaji tersimpan utuh di database setelah kalkulasi selesai"""
        
        # Eksekusi kalkulasi payroll untuk bulan Juni tahun 2026
        payslip = self.payroll_service.calculate_monthly_payroll(self.employee.id, 6, 2026)
        
        # Pastikan record slip gaji sukses terbuat di database
        self.assertTrue(payslip, "Slip gaji gagal digenerate.")
        self.assertEqual(payslip.x_gross_salary, 10000000.0)
        self.assertEqual(payslip.x_pph21_amount, 200000.0)
        
        # Net Salary = Gross (10jt) - Pajak (200rb) - Potongan BPJS (asumsi di service masih 0 atau disesuaikan)
        expected_net = 10000000.0 - 200000.0 - payslip.x_bpjs_deduction
        self.assertEqual(payslip.x_net_salary, expected_net, "Kalkulasi Net Salary meleset!")