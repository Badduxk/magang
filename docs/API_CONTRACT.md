# API_CONTRACT.md

# HRIS ODOO 19

## API CONTRACT DOCUMENT

Version: 1.1
Status: Revised — Kontradiksi telah diselesaikan
Tanggal Revisi: Juni 2026

---

# OVERVIEW

Dokumen ini mendefinisikan kontrak API antara:

* Backend Odoo
* Frontend Admin (HR Admin)
* Frontend User (Karyawan — Portal)
* Mobile Application
* WhatsApp Service
* Fingerprint Service

Tujuan:

* Menyamakan struktur request dan response antar tim.
* Menjadi referensi tunggal seluruh tim pengembang.
* Menjadi referensi AI Assistant (Copilot, Claude Code, Cursor, Antigravity).

---

# API STANDARD

## Base URL

```http
/api/v1
```

---

## Response Success

```json
{
    "success": true,
    "message": "Success",
    "data": {}
}
```

---

## Response Error

```json
{
    "success": false,
    "message": "Pesan error yang jelas dan dapat dipahami",
    "errors": [
        {
            "field": "nama_field",
            "message": "Detail error pada field ini"
        }
    ]
}
```

---

## HTTP Status Code

| Code | Deskripsi             | Kapan Digunakan                              |
| ---- | --------------------- | -------------------------------------------- |
| 200  | OK                    | Request berhasil, data dikembalikan          |
| 201  | Created               | Data baru berhasil dibuat                    |
| 400  | Bad Request           | Request tidak valid (format salah)           |
| 401  | Unauthorized          | Token tidak ada atau tidak valid             |
| 403  | Forbidden             | Token valid tapi tidak punya akses           |
| 404  | Not Found             | Data yang diminta tidak ditemukan            |
| 422  | Unprocessable Entity  | Validasi bisnis gagal (misal: kuota habis)   |
| 500  | Internal Server Error | Error di sisi server                         |

---

# AUTHENTICATION

## Login

### Endpoint

```http
POST /api/v1/auth/login
```

### Role yang Bisa Akses

* Karyawan
* HR Admin

> Pimpinan tidak memiliki akun dan tidak bisa login.

### Request Body

```json
{
    "username": "employee01",
    "password": "password123"
}
```

### Response Success (200)

```json
{
    "success": true,
    "message": "Login berhasil",
    "data": {
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "employee_id": 1,
        "full_name": "Budi Santoso",
        "role": "employee",
        "employee_type": "tetap"
    }
}
```

### Response Error — Salah Password (401)

```json
{
    "success": false,
    "message": "Username atau password salah",
    "errors": []
}
```

---

## Logout

### Endpoint

```http
POST /api/v1/auth/logout
```

### Role yang Bisa Akses

* Karyawan
* HR Admin

### Response Success (200)

```json
{
    "success": true,
    "message": "Logout berhasil",
    "data": {}
}
```

---

## Current User (Profil Login)

### Endpoint

```http
GET /api/v1/auth/me
```

### Role yang Bisa Akses

* Karyawan
* HR Admin

### Response Success (200)

```json
{
    "success": true,
    "message": "Success",
    "data": {
        "user_id": 1,
        "employee_id": 10,
        "full_name": "Budi Santoso",
        "email": "budi@company.com",
        "role": "employee",
        "employee_type": "tetap",
        "department": "Engineering",
        "job_position": "Backend Developer"
    }
}
```

---

# EMPLOYEE

## Lihat Profil Sendiri

### Endpoint

```http
GET /api/v1/employees/me
```

### Role yang Bisa Akses

* Karyawan

### Response Success (200)

```json
{
    "success": true,
    "message": "Success",
    "data": {
        "employee_id": 10,
        "employee_code": "EMP-0010",
        "nik": "3201234567890001",
        "full_name": "Budi Santoso",
        "email": "budi@company.com",
        "phone_number": "08123456789",
        "employee_type": "tetap",
        "department": "Engineering",
        "job_position": "Backend Developer",
        "join_date": "2023-01-15",
        "status": "active"
    }
}
```

---

## Update Profil Sendiri

### Endpoint

```http
PUT /api/v1/employees/me
```

### Role yang Bisa Akses

* Karyawan

### Request Body

```json
{
    "phone_number": "08987654321",
    "bank_name": "BCA",
    "bank_account_number": "1234567890"
}
```

### Response Success (200)

```json
{
    "success": true,
    "message": "Profil berhasil diperbarui",
    "data": {
        "employee_id": 10,
        "phone_number": "08987654321",
        "bank_name": "BCA",
        "bank_account_number": "1234567890",
        "updated_at": "2026-06-24 10:00:00"
    }
}
```

---

## Daftar Semua Karyawan

### Endpoint

```http
GET /api/v1/employees
```

### Role yang Bisa Akses

* HR Admin

### Query Parameters

```
page          → Nomor halaman (default: 1)
per_page      → Jumlah data per halaman (default: 20)
department_id → Filter berdasarkan departemen
employee_type → Filter berdasarkan tipe: tetap / freelance
status        → Filter berdasarkan status: active / inactive / resigned
search        → Cari berdasarkan nama atau employee_code
```

### Response Success (200)

```json
{
    "success": true,
    "message": "Success",
    "data": {
        "total": 50,
        "page": 1,
        "per_page": 20,
        "employees": [
            {
                "employee_id": 10,
                "employee_code": "EMP-0010",
                "full_name": "Budi Santoso",
                "employee_type": "tetap",
                "department": "Engineering",
                "job_position": "Backend Developer",
                "status": "active"
            }
        ]
    }
}
```

---

## Detail Karyawan

### Endpoint

```http
GET /api/v1/employees/{employee_id}
```

### Role yang Bisa Akses

* HR Admin

---

## Tambah Karyawan

### Endpoint

```http
POST /api/v1/employees
```

### Role yang Bisa Akses

* HR Admin

### Request Body

```json
{
    "nik": "3201234567890001",
    "full_name": "Ani Wijaya",
    "email": "ani@company.com",
    "phone_number": "08111222333",
    "employee_type": "tetap",
    "department_id": 3,
    "job_position": "HR Officer",
    "npwp_number": "12.345.678.9-001.000",
    "bank_name": "Mandiri",
    "bank_account_number": "9876543210",
    "join_date": "2026-07-01"
}
```

---

## Edit Karyawan

### Endpoint

```http
PUT /api/v1/employees/{employee_id}
```

### Role yang Bisa Akses

* HR Admin

---

## Hapus Karyawan (Soft Delete)

### Endpoint

```http
DELETE /api/v1/employees/{employee_id}
```

### Role yang Bisa Akses

* HR Admin

> Catatan: Tidak benar-benar menghapus data. Mengubah `status` menjadi `resigned`
> dan `active` menjadi `False` di Odoo (soft delete).

---

# ATTENDANCE

## Riwayat Absensi Sendiri

### Endpoint

```http
GET /api/v1/attendance/me
```

### Role yang Bisa Akses

* Karyawan

### Query Parameters

```
month     → Filter bulan (format: YYYY-MM, default: bulan ini)
page      → Nomor halaman
per_page  → Jumlah per halaman
```

### Response Success (200)

```json
{
    "success": true,
    "message": "Success",
    "data": {
        "employee_id": 10,
        "month": "2026-06",
        "summary": {
            "total_hadir": 18,
            "total_izin": 1,
            "total_cuti": 0,
            "total_sakit": 0,
            "total_alpha": 0,
            "total_overtime_hours": 6.5
        },
        "records": [
            {
                "attendance_id": 100,
                "attendance_date": "2026-06-24",
                "check_in": "2026-06-24 08:05:00",
                "check_out": "2026-06-24 17:30:00",
                "worked_hours": 9.42,
                "overtime_hours": 1.42,
                "attendance_status": "hadir"
            }
        ]
    }
}
```

---

## Detail Absensi

### Endpoint

```http
GET /api/v1/attendance/{attendance_id}
```

### Role yang Bisa Akses

* Karyawan (hanya milik sendiri)
* HR Admin (semua karyawan)

---

## Daftar Semua Absensi

### Endpoint

```http
GET /api/v1/attendance
```

### Role yang Bisa Akses

* HR Admin

### Query Parameters

```
month         → Filter bulan (YYYY-MM)
employee_id   → Filter karyawan tertentu
department_id → Filter departemen
status        → Filter status: hadir / izin / cuti / sakit / alpha
page          → Nomor halaman
per_page      → Jumlah per halaman
```

---

## Ringkasan Absensi

### Endpoint

```http
GET /api/v1/attendance/summary
```

### Role yang Bisa Akses

* HR Admin

### Query Parameters

```
month → Bulan yang ingin dirangkum (YYYY-MM)
```

### Response Success (200)

```json
{
    "success": true,
    "message": "Success",
    "data": {
        "month": "2026-06",
        "total_karyawan": 50,
        "rata_kehadiran": "94%",
        "total_alpha": 3,
        "total_overtime_hours": 145.5,
        "by_department": [
            {
                "department": "Engineering",
                "hadir": 18,
                "alpha": 1,
                "izin": 2
            }
        ]
    }
}
```

---

## Koreksi Absensi Manual

### Endpoint

```http
POST /api/v1/attendance/correction
```

### Role yang Bisa Akses

* HR Admin

### Request Body

```json
{
    "employee_id": 10,
    "attendance_date": "2026-06-24",
    "check_in": "2026-06-24 08:00:00",
    "check_out": "2026-06-24 17:00:00",
    "reason": "Fingerprint error pada hari tersebut"
}
```

### Response Success (201)

```json
{
    "success": true,
    "message": "Koreksi absensi berhasil disimpan",
    "data": {
        "attendance_id": 105,
        "employee_id": 10,
        "attendance_date": "2026-06-24",
        "check_in": "2026-06-24 08:00:00",
        "check_out": "2026-06-24 17:00:00",
        "worked_hours": 9.0,
        "overtime_hours": 1.0,
        "source": "manual"
    }
}
```

---

# LEAVE (IZIN)

> **Catatan Arsitektur:**
> Endpoint `/api/v1/leaves` dan `/api/v1/time-off` menggunakan **model yang sama di backend**
> yaitu `hr.leave`. Pembeda adalah `leave_type` yang dikirim di request body.
> Pemisahan endpoint dilakukan agar lebih mudah dipahami oleh developer frontend.

---

## Ajukan Izin

### Endpoint

```http
POST /api/v1/leaves
```

### Role yang Bisa Akses

* Karyawan

### Request Body

```json
{
    "leave_type": "izin",
    "start_date": "2026-06-25",
    "end_date": "2026-06-25",
    "reason": "Keperluan keluarga mendesak",
    "attachment": "(base64 encoded file — opsional)"
}
```

> `attachment` bersifat **opsional** untuk izin. Boleh dikosongkan atau tidak disertakan.

### Response Success (201)

```json
{
    "success": true,
    "message": "Pengajuan izin berhasil dikirim",
    "data": {
        "leave_id": 50,
        "leave_type": "izin",
        "start_date": "2026-06-25",
        "end_date": "2026-06-25",
        "total_days": 1,
        "reason": "Keperluan keluarga mendesak",
        "approval_status": "pending",
        "created_at": "2026-06-24 09:00:00"
    }
}
```

### Response Error — Kuota Habis (422)

```json
{
    "success": false,
    "message": "Sisa kuota cuti tidak mencukupi",
    "errors": [
        {
            "field": "leave_type",
            "message": "Kuota cuti tersisa 0 hari. Tidak dapat mengajukan izin."
        }
    ]
}
```

---

## Daftar Semua Izin

### Endpoint

```http
GET /api/v1/leaves
```

### Role yang Bisa Akses

* HR Admin

### Query Parameters

```
month           → Filter bulan (YYYY-MM)
employee_id     → Filter karyawan tertentu
approval_status → Filter status: pending / approved / rejected / cancelled
page            → Nomor halaman
per_page        → Jumlah per halaman
```

---

## Izin Saya

### Endpoint

```http
GET /api/v1/leaves/me
```

### Role yang Bisa Akses

* Karyawan

---

## Detail Izin

### Endpoint

```http
GET /api/v1/leaves/{leave_id}
```

### Role yang Bisa Akses

* Karyawan (hanya milik sendiri)
* HR Admin (semua karyawan)

---

## Daftar Leave Type

### Endpoint

```http
GET /api/v1/leaves/types
```

### Role yang Bisa Akses

* Karyawan
* HR Admin

### Response Success (200)

```json
{
    "success": true,
    "message": "Success",
    "data": [
        {
            "leave_type": "izin",
            "label": "Izin",
            "requires_attachment": false,
            "deducts_quota": true,
            "available_for": ["tetap", "freelance"]
        },
        {
            "leave_type": "cuti",
            "label": "Cuti",
            "requires_attachment": false,
            "deducts_quota": true,
            "available_for": ["tetap"]
        },
        {
            "leave_type": "sakit",
            "label": "Sakit",
            "requires_attachment": true,
            "deducts_quota": false,
            "available_for": ["tetap", "freelance"]
        }
    ]
}
```

---

## Approve Izin

### Endpoint

```http
POST /api/v1/leaves/{leave_id}/approve
```

### Role yang Bisa Akses

* HR Admin

### Response Success (200)

```json
{
    "success": true,
    "message": "Pengajuan izin telah disetujui",
    "data": {
        "leave_id": 50,
        "approval_status": "approved",
        "approved_by": 2,
        "approved_at": "2026-06-24 10:30:00"
    }
}
```

---

## Reject Izin

### Endpoint

```http
POST /api/v1/leaves/{leave_id}/reject
```

### Role yang Bisa Akses

* HR Admin

### Request Body

```json
{
    "reject_reason": "Staf tidak mencukupi pada tanggal tersebut"
}
```

---

# MEDICAL CERTIFICATE (SURAT DOKTER)

## Upload Surat Dokter

### Endpoint

```http
POST /api/v1/medical-certificates
```

### Role yang Bisa Akses

* Karyawan

### Request Body

```json
{
    "leave_id": 55,
    "file_attachment": "(base64 encoded PDF atau gambar — WAJIB)"
}
```

> `file_attachment` bersifat **wajib**. Pengajuan sakit tanpa surat dokter akan ditolak.

### Response Success (201)

```json
{
    "success": true,
    "message": "Surat dokter berhasil diupload",
    "data": {
        "certificate_id": 10,
        "leave_id": 55,
        "approval_status": "pending",
        "created_at": "2026-06-24 09:00:00"
    }
}
```

---

## Approve Surat Dokter

### Endpoint

```http
POST /api/v1/medical-certificates/{id}/approve
```

### Role yang Bisa Akses

* HR Admin

---

## Reject Surat Dokter

### Endpoint

```http
POST /api/v1/medical-certificates/{id}/reject
```

### Role yang Bisa Akses

* HR Admin

### Request Body

```json
{
    "reject_reason": "Surat dokter tidak terbaca atau tidak valid"
}
```

---

# TIME OFF (CUTI & SAKIT)

> **Catatan Arsitektur:**
> Endpoint ini menggunakan model `hr.leave` yang sama dengan `/api/v1/leaves`.
> Pembeda adalah `leave_type` di request body.

---

## Ajukan Cuti / Sakit

### Endpoint

```http
POST /api/v1/time-off
```

### Role yang Bisa Akses

* Karyawan

### Request Body untuk Cuti

```json
{
    "leave_type": "cuti",
    "start_date": "2026-07-01",
    "end_date": "2026-07-05",
    "reason": "Liburan keluarga"
}
```

### Request Body untuk Sakit

```json
{
    "leave_type": "sakit",
    "start_date": "2026-06-25",
    "end_date": "2026-06-26",
    "reason": "Demam dan flu",
    "attachment": "(base64 encoded file surat dokter — WAJIB untuk sakit)"
}
```

### Response Success (201)

```json
{
    "success": true,
    "message": "Pengajuan cuti berhasil dikirim",
    "data": {
        "leave_id": 60,
        "leave_type": "cuti",
        "start_date": "2026-07-01",
        "end_date": "2026-07-05",
        "total_days": 5,
        "approval_status": "pending",
        "created_at": "2026-06-24 11:00:00"
    }
}
```

### Response Error — Freelance Ajukan Cuti (422)

```json
{
    "success": false,
    "message": "Karyawan freelance tidak memiliki hak cuti",
    "errors": [
        {
            "field": "leave_type",
            "message": "Tipe karyawan 'freelance' tidak dapat mengajukan cuti."
        }
    ]
}
```

### Response Error — Sakit Tanpa Surat Dokter (422)

```json
{
    "success": false,
    "message": "Surat dokter wajib dilampirkan untuk pengajuan sakit",
    "errors": [
        {
            "field": "attachment",
            "message": "Field attachment wajib diisi untuk leave_type=sakit."
        }
    ]
}
```

---

## Cuti / Sakit Saya

### Endpoint

```http
GET /api/v1/time-off/me
```

### Role yang Bisa Akses

* Karyawan

---

## Approve Cuti / Sakit

### Endpoint

```http
POST /api/v1/time-off/{id}/approve
```

### Role yang Bisa Akses

* HR Admin

---

## Reject Cuti / Sakit

### Endpoint

```http
POST /api/v1/time-off/{id}/reject
```

### Role yang Bisa Akses

* HR Admin

### Request Body

```json
{
    "reject_reason": "Alasan penolakan yang jelas"
}
```

---

# PAYROLL

Status:

```
PENDING AUDIT — Modul payroll Odoo belum dikonfirmasi ketersediaannya.
Endpoint berikut adalah rencana awal dan dapat berubah setelah audit.
```

---

## Daftar Payroll

### Endpoint

```http
GET /api/v1/payroll
```

### Role yang Bisa Akses

* HR Admin

### Query Parameters

```
year      → Filter tahun
month     → Filter bulan (1-12)
status    → Filter status: draft / generated / paid / cancelled
page      → Nomor halaman
per_page  → Jumlah per halaman
```

---

## Detail Payroll

### Endpoint

```http
GET /api/v1/payroll/{payroll_id}
```

### Role yang Bisa Akses

* HR Admin

### Response Success (200)

```json
{
    "success": true,
    "message": "Success",
    "data": {
        "payroll_id": 100,
        "employee_id": 10,
        "full_name": "Budi Santoso",
        "payroll_month": 6,
        "payroll_year": 2026,
        "basic_salary": 8000000,
        "overtime_amount": 500000,
        "allowance_amount": 1000000,
        "alpha_deduction": 0,
        "pph21_amount": 150000,
        "total_salary": 9350000,
        "payroll_status": "generated",
        "generated_at": "2026-06-27 14:00:00"
    }
}
```

---

## Generate Payroll

### Endpoint

```http
POST /api/v1/payroll/generate
```

### Role yang Bisa Akses

* HR Admin

### Request Body

```json
{
    "month": 6,
    "year": 2026
}
```

### Response Success (201)

```json
{
    "success": true,
    "message": "Payroll bulan Juni 2026 berhasil di-generate",
    "data": {
        "generated_count": 50,
        "month": 6,
        "year": 2026,
        "generated_at": "2026-06-27 14:00:00"
    }
}
```

---

# PAYSLIP

## Slip Gaji Saya

### Endpoint

```http
GET /api/v1/payslips/me
```

### Role yang Bisa Akses

* Karyawan

### Query Parameters

```
year → Filter tahun (default: tahun ini)
```

### Response Success (200)

```json
{
    "success": true,
    "message": "Success",
    "data": [
        {
            "payslip_id": 200,
            "payroll_month": 6,
            "payroll_year": 2026,
            "total_salary": 9350000,
            "payroll_status": "paid",
            "created_at": "2026-06-27 14:00:00"
        }
    ]
}
```

---

## Download Slip Gaji

### Endpoint

```http
GET /api/v1/payslips/{id}/download
```

### Role yang Bisa Akses

* Karyawan (hanya milik sendiri)
* HR Admin (semua karyawan)

### Response

```
File PDF slip gaji (Content-Type: application/pdf)
```

---

## Kirim Notifikasi WhatsApp Slip Gaji

### Endpoint

```http
POST /api/v1/payslips/{id}/whatsapp
```

### Role yang Bisa Akses

* HR Admin

### Response Success (200)

```json
{
    "success": true,
    "message": "Notifikasi WhatsApp slip gaji berhasil dikirim",
    "data": {
        "payslip_id": 200,
        "employee_id": 10,
        "phone_number": "08123456789",
        "whatsapp_sent": true,
        "sent_at": "2026-06-27 15:00:00"
    }
}
```

> **Catatan:** Tidak ada endpoint kirim via email. Sistem hanya menggunakan WhatsApp.

---

# FINGERPRINT

## Status Device Fingerprint

### Endpoint

```http
GET /api/v1/fingerprint/status
```

### Role yang Bisa Akses

* HR Admin

### Response Success (200)

```json
{
    "success": true,
    "message": "Success",
    "data": {
        "device_id": 1,
        "device_name": "Magic Fingerprint - Lobby",
        "status": "online",
        "last_sync_at": "2026-06-24 08:30:00",
        "pending_logs": 0
    }
}
```

---

## Sinkronisasi Manual Fingerprint

### Endpoint

```http
POST /api/v1/fingerprint/sync
```

### Role yang Bisa Akses

* HR Admin

### Response Success (200)

```json
{
    "success": true,
    "message": "Sinkronisasi berhasil",
    "data": {
        "synced_logs": 25,
        "generated_attendance": 25,
        "failed_logs": 0,
        "sync_time": "2026-06-24 09:00:00"
    }
}
```

---

## Log Fingerprint

### Endpoint

```http
GET /api/v1/fingerprint/logs
```

### Role yang Bisa Akses

* HR Admin

### Query Parameters

```
date        → Filter tanggal (YYYY-MM-DD)
sync_status → Filter status: pending / success / failed
page        → Nomor halaman
per_page    → Jumlah per halaman
```

---

## Mapping Fingerprint ke Karyawan

### Endpoint

```http
POST /api/v1/fingerprint/mapping
```

### Role yang Bisa Akses

* HR Admin

### Request Body

```json
{
    "employee_id": 10,
    "fingerprint_id": "FP-00123"
}
```

---

# WHATSAPP

## Kirim Pesan Manual

### Endpoint

```http
POST /api/v1/whatsapp/send
```

### Role yang Bisa Akses

* HR Admin

### Request Body

```json
{
    "phone_number": "08123456789",
    "message": "Isi pesan yang akan dikirim"
}
```

---

## Kirim Laporan Harian ke Pimpinan

### Endpoint

```http
POST /api/v1/whatsapp/report/daily
```

### Role yang Bisa Akses

* HR Admin

### Request Body

```json
{
    "date": "2026-06-24"
}
```

### Response Success (200)

```json
{
    "success": true,
    "message": "Laporan harian berhasil dikirim ke pimpinan",
    "data": {
        "date": "2026-06-24",
        "recipients": ["0812xxxxxx"],
        "sent_at": "2026-06-24 18:00:00"
    }
}
```

---

## Kirim Laporan Bulanan ke Pimpinan

### Endpoint

```http
POST /api/v1/whatsapp/report/monthly
```

### Role yang Bisa Akses

* HR Admin

### Request Body

```json
{
    "month": 6,
    "year": 2026
}
```

---

# REPORTING

## Laporan Absensi Harian

### Endpoint

```http
GET /api/v1/reports/attendance/daily
```

### Role yang Bisa Akses

* HR Admin

### Query Parameters

```
date → Tanggal yang ingin dilaporkan (YYYY-MM-DD, default: hari ini)
```

---

## Laporan Absensi Bulanan

### Endpoint

```http
GET /api/v1/reports/attendance/monthly
```

### Role yang Bisa Akses

* HR Admin

### Query Parameters

```
month → Bulan (1-12)
year  → Tahun
```

---

## Laporan Izin/Cuti/Sakit

### Endpoint

```http
GET /api/v1/reports/leaves
```

### Role yang Bisa Akses

* HR Admin

### Query Parameters

```
month       → Bulan (1-12)
year        → Tahun
leave_type  → Filter: izin / cuti / sakit
```

---

## Laporan Payroll

### Endpoint

```http
GET /api/v1/reports/payroll
```

### Role yang Bisa Akses

* HR Admin

### Query Parameters

```
month → Bulan (1-12)
year  → Tahun
```

---

# DASHBOARD

## Dashboard Karyawan

### Endpoint

```http
GET /api/v1/dashboard/employee
```

### Role yang Bisa Akses

* Karyawan

### Response Success (200)

```json
{
    "success": true,
    "message": "Success",
    "data": {
        "employee_id": 10,
        "full_name": "Budi Santoso",
        "this_month": {
            "total_hadir": 18,
            "total_alpha": 0,
            "total_izin": 1,
            "total_cuti": 0,
            "total_overtime_hours": 6.5
        },
        "leave_balance": {
            "total_quota": 12,
            "used_quota": 3,
            "remaining_quota": 9
        },
        "pending_requests": 0,
        "latest_payslip": {
            "month": 5,
            "year": 2026,
            "total_salary": 9350000
        }
    }
}
```

---

## Dashboard HR Admin

### Endpoint

```http
GET /api/v1/dashboard/hr-admin
```

### Role yang Bisa Akses

* HR Admin

### Response Success (200)

```json
{
    "success": true,
    "message": "Success",
    "data": {
        "today": "2026-06-24",
        "total_karyawan_aktif": 50,
        "kehadiran_hari_ini": {
            "hadir": 45,
            "izin": 2,
            "cuti": 1,
            "sakit": 1,
            "alpha": 1
        },
        "pending_approvals": {
            "izin": 2,
            "cuti": 1,
            "sakit": 0
        },
        "fingerprint_status": "online",
        "last_sync": "2026-06-24 08:30:00"
    }
}
```

---

# FUTURE API (BELUM DITENTUKAN)

Endpoint berikut belum dapat didefinisikan karena menunggu keputusan bisnis atau audit teknis:

| Endpoint                    | Alasan Pending                          |
| --------------------------- | --------------------------------------- |
| Payroll Formula Detail      | Menunggu audit modul Payroll Odoo       |
| BPJS Integration            | Menunggu keputusan bisnis               |
| THR Calculation             | Menunggu keputusan bisnis               |
| Multi Branch Support        | Menunggu keputusan bisnis               |
| Mobile Application API      | Menunggu keputusan platform mobile      |
| WhatsApp Provider Specific  | Menunggu pemilihan provider WhatsApp    |

> **Catatan:** Tidak ada endpoint pengiriman via email yang direncanakan.
> Seluruh notifikasi akan menggunakan WhatsApp.