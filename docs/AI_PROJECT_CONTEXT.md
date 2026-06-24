# AI_PROJECT_CONTEXT.md

# HRIS ODOO 19 — PROJECT CONTEXT

Version: 1.1
Status: Revised — Kontradiksi telah diselesaikan
Tanggal Revisi: Juni 2026

---

# CATATAN REVISI

Perubahan dari versi 1.0:

1. Ditambahkan klarifikasi bahwa HR Admin tetap bisa absensi via fingerprint.
2. Dihapus referensi email — notifikasi hanya WhatsApp.
3. Diseragamkan istilah status Leave: menggunakan `pending` sebagai status awal.
4. Ditambahkan aturan validasi freelance tidak bisa cuti.
5. Ditambahkan catatan bahwa WhatsApp provider wajib ditentukan sebelum implementasi hris_whatsapp.
6. Diperjelas bahwa Leave dan Time Off di API menggunakan satu model yang sama di backend.
7. Ditambahkan definisi formula alpha_deduction dan pph21.

---

# PROJECT OVERVIEW

Project Name:

```
HRIS (Human Resource Information System)
```

Platform:

```
Odoo 19 Community
```

Architecture:

```
Modular Architecture — Extend First, Custom If Needed
```

Development Approach:

```
1. Extend Existing Odoo Modules
2. Custom Module Only If Required
3. Never Modify Odoo Core
```

---

# PROJECT OBJECTIVE

Membangun template HRIS yang dapat digunakan oleh banyak perusahaan
tanpa mengubah source code utama Odoo.

Semua kebutuhan perusahaan harus diimplementasikan melalui:

* Extend Module Odoo
* Configuration
* Custom Module

Tidak boleh memodifikasi core Odoo.

---

# PROJECT PRINCIPLE

AI WAJIB MEMATUHI SELURUH RULE BERIKUT.

Jika terdapat konflik antar dokumen, urutan prioritas adalah:

1. BUSINESS_FLOW.md
2. MODULE_MAPPING.md
3. DATA_DICTIONARY.md
4. API_CONTRACT.md

AI tidak boleh membuat asumsi sendiri di luar dokumen-dokumen ini.

---

# DEVELOPMENT STRATEGY

Prioritas pengembangan (urutan dari yang paling diutamakan):

1. Extend Existing Odoo Module
2. Extend Existing Odoo Model
3. Extend Existing Odoo View
4. Create New Model
5. Create New Module

AI tidak boleh langsung membuat modul baru sebelum memeriksa MODULE_MAPPING.md.

---

# PROJECT MODULE STRUCTURE

```
addons/
├── hris_base
├── hris_employee
├── hris_attendance
├── hris_timeoff
├── hris_payroll
├── hris_fingerprint
├── hris_whatsapp
├── hris_notification
├── hris_portal
└── hris_reporting
```

---

# MODULE DEPENDENCY

```yaml
hris_base:
  depends: []

hris_employee:
  depends:
    - hr
    - hris_base

hris_attendance:
  depends:
    - hr_attendance
    - hris_employee

hris_timeoff:
  depends:
    - hr_holidays
    - hris_employee

hris_payroll:
  depends:
    - hris_employee
    - hris_attendance
    - hris_timeoff

hris_fingerprint:
  depends:
    - hris_attendance

hris_whatsapp:
  depends:
    - hris_base

hris_notification:
  depends:
    - hris_whatsapp

hris_portal:
  depends:
    - portal
    - hris_employee
    - hris_attendance
    - hris_timeoff

hris_reporting:
  depends:
    - hris_employee
    - hris_attendance
    - hris_timeoff
    - hris_payroll
```

---

# BUSINESS RULES

## Employee Type

Hanya dua tipe karyawan yang diakui sistem:

```
tetap       → Karyawan Tetap
freelance   → Karyawan Freelance
```

Tidak ada tipe karyawan lain.

---

## Attendance (Absensi)

Sumber absensi:

```
Mesin Fingerprint — SATU-SATUNYA sumber absensi yang valid
```

Absensi manual:

```
TIDAK DIIZINKAN untuk karyawan biasa.
Koreksi manual hanya bisa dilakukan oleh HR Admin di backend sistem.
```

Metode absensi karyawan:

```
Check In  → scan fingerprint pertama di hari tersebut
Check Out → scan fingerprint terakhir di hari tersebut
```

Catatan untuk HR Admin:

```
HR Admin juga adalah karyawan perusahaan.
HR Admin melakukan absensi via fingerprint seperti karyawan lain.
HR Admin tidak memiliki akses tombol atau form absensi manual di UI.
```

Kiosk Mode Odoo:

```
DINONAKTIFKAN — tidak digunakan sebagai metode absensi.
Absensi hanya melalui integrasi fingerprint via hris_fingerprint.
```

---

## Working Hour (Jam Kerja)

Target jam kerja per hari:

```
8 Jam
```

Aturan:

```
worked_hours < 8 jam   → Normal (tidak ada potongan, tidak ada lembur)
worked_hours = 8 jam   → Selesai tepat waktu
worked_hours > 8 jam   → Lembur (otomatis dihitung)
```

---

## Late Detection (Keterlambatan)

Keterlambatan dideteksi berdasarkan:

```
Jadwal kerja (resource.calendar) yang ditetapkan untuk karyawan
```

Namun keterlambatan saat ini:

```
- Tidak dicatat sebagai field terpisah di sistem
- Tidak memerlukan approval
- Hanya terlihat dari selisih check_in vs jam masuk di jadwal kerja
```

---

## Overtime (Lembur)

Lembur dihitung otomatis oleh sistem — tidak ada pengajuan oleh karyawan.

Aturan:

```
overtime_hours = worked_hours - 8  (hanya jika worked_hours > 8)
```

Nominal lembur:

```
overtime_amount = overtime_hours × (basic_salary / 173)

Keterangan:
173 = standar jam kerja bulanan (8 jam × 21.75 hari)
Nilai ini dihitung saat generate payroll, bukan real-time.
```

Contoh:

```
Check in 08:00, Check out 18:00
worked_hours = 10 jam
overtime_hours = 10 - 8 = 2 jam lembur
```

---

## Leave (Pengajuan Izin, Cuti, Sakit)

Model yang digunakan:

```
hr.leave (Odoo native, di-extend)
```

Satu model untuk ketiga jenis pengajuan.
Pembeda adalah Leave Type (hr.leave.type):

```
Leave Type IZIN  → izin tidak masuk (lampiran opsional, potong kuota)
Leave Type CUTI  → cuti tahunan (tanpa lampiran, potong kuota, khusus tetap)
Leave Type SAKIT → sakit (lampiran wajib, tidak potong kuota)
```

Status awal semua pengajuan:

```
pending  (bukan on_proses, bukan waiting)
```

Status mapping ke Odoo internal:

```
pending   → to_approve
approved  → approved
rejected  → refused
cancelled → cancel
```

Aturan validasi yang wajib diimplementasikan:

```
1. Jika Leave Type = CUTI dan employee_type = freelance
   → Tolak dengan pesan: "Karyawan freelance tidak memiliki hak cuti"

2. Jika Leave Type = SAKIT dan attachment kosong
   → Tolak dengan pesan: "Surat dokter wajib dilampirkan"

3. Jika Leave Type = IZIN atau CUTI dan remaining_quota = 0
   → Tolak dengan pesan: "Sisa kuota cuti tidak mencukupi"
```

Workflow approval:

```
Satu level saja — karyawan mengajukan, HR Admin approve/reject.
Tidak ada multi-level approval.
```

---

## Sick Leave (Sakit)

Karyawan yang sakit wajib:

```
1. Membuat pengajuan dengan Leave Type = SAKIT
2. Melampirkan surat dokter atau bukti medis (WAJIB)
```

Tanpa lampiran:

```
Sistem menolak pengajuan secara otomatis.
```

---

## Payroll

Periode payroll:

```
Bulanan
```

Tanggal penggajian:

```
Tanggal 28 setiap bulan
```

Sumber data payroll:

```
- Data karyawan (kontrak: gaji pokok, tunjangan)
- Attendance bulan tersebut (untuk hitung alpha dan lembur)
- Leave Request yang approved (untuk status kehadiran)
- Overtime yang dihitung otomatis
```

Formula alpha_deduction:

```
alpha_deduction = jumlah_hari_alpha × (basic_salary / hari_kerja_bulan_ini)

Keterangan:
- jumlah_hari_alpha: total hari dengan attendance_status = alpha
- hari_kerja_bulan_ini: total hari kerja (tidak termasuk weekend dan libur nasional)
```

Formula pph21_amount:

```
1. Hitung penghasilan bruto bulanan = gaji pokok + lembur + tunjangan
2. Estimasi penghasilan bruto tahunan = bruto bulanan × 12
3. Hitung PKP = bruto tahunan - PTKP
4. Hitung PPh21 tahunan menggunakan tarif progresif:
      PKP ≤ 60 juta       → 5%
      60–250 juta         → 15%
      250–500 juta        → 25%
      500 juta–5 miliar   → 30%
      > 5 miliar          → 35%
5. PPh21 bulanan = PPh21 tahunan / 12
```

Total gaji bersih:

```
total_salary = basic_salary + overtime_amount + allowance_amount
             - alpha_deduction - pph21_amount
```

---

## Approval Authority (Pihak yang Menyetujui)

Semua approval dilakukan oleh **HR Admin**.

Proses yang memerlukan approval:

```
- Pengajuan izin
- Pengajuan cuti (karyawan tetap)
- Pengajuan sakit
- Koreksi data absensi
```

Tidak ada multi-level approval.
Tidak ada approval via WhatsApp (notifikasi saja, keputusan tetap di sistem).

---

## Notification (Notifikasi)

Saluran notifikasi:

```
WhatsApp — SATU-SATUNYA saluran notifikasi
```

Email:

```
TIDAK DIGUNAKAN — tidak ada notifikasi via email di sistem ini
```

Ini berlaku untuk semua notifikasi termasuk:

```
- Notifikasi absensi ke karyawan
- Notifikasi pengajuan ke HR Admin
- Notifikasi approval/reject ke karyawan
- Notifikasi slip gaji ke karyawan
- Laporan ke pimpinan
```

---

## Reporting (Laporan)

Laporan yang diperlukan:

```
- Rekap absensi harian
- Rekap absensi bulanan
- Rekap izin/cuti/sakit
- Rekap lembur
- Rekap payroll
```

Dashboard:

```
HR Dashboard  → Diperlukan (untuk HR Admin)
Manager Dashboard → Tidak diperlukan
Director Dashboard → Tidak diperlukan
```

Laporan ke pimpinan:

```
Dikirim otomatis via WhatsApp (bukan dashboard).
Format: pesan teks ringkasan harian dan bulanan.
```

---

# FINGERPRINT RULES

Mesin yang digunakan:

```
Magic Fingerprint
```

Jumlah mesin:

```
1 unit
```

Mode sinkronisasi:

```
Real-time jika online
```

Fallback jika offline:

```
Data disimpan di mesin lokal.
Sinkronisasi otomatis dilakukan saat koneksi tersambung kembali.
```

---

# WHATSAPP RULES

Status provider:

```
TBD (To Be Determined) — wajib dipilih sebelum implementasi hris_whatsapp dimulai
```

> **BLOCKER:** Implementasi modul hris_whatsapp tidak dapat dimulai sebelum provider dipilih.
> Pilihan provider akan mempengaruhi struktur request/response di adapter layer.
>
> Keputusan pemilihan provider adalah tanggung jawab Product Owner / Project Manager.

Fitur yang wajib didukung provider:

```
- Kirim pesan teks biasa ke nomor individual
- Template message (untuk laporan terstruktur)
- Pengiriman ke banyak nomor sekaligus (untuk notifikasi massal)
- API yang terdokumentasi dengan baik
```

Approval via WhatsApp:

```
TIDAK DIPERLUKAN — WhatsApp hanya untuk notifikasi, bukan untuk proses approval.
Semua approval tetap dilakukan di dalam sistem (web atau portal).
```

---

# PORTAL RULES

Portal karyawan diperlukan dengan fitur:

Login:

```
Username + Password
```

Karyawan dapat:

```
- Lihat profil sendiri
- Update profil sendiri
- Lihat riwayat absensi sendiri
- Ajukan izin / cuti / sakit
- Lihat status pengajuan
- Download slip gaji
```

Karyawan tidak dapat:

```
- Melihat data karyawan lain
- Mengakses fitur HR Admin
- Mengoreksi data absensi
```

---

# DATABASE RULES

Setiap model Odoo yang dibuat atau di-extend wajib mengandung field standar:

```
active
company_id
create_uid
create_date
write_uid
write_date
```

Soft delete diutamakan:

```
Gunakan field active = False untuk menonaktifkan record.
Hindari hard delete (DELETE FROM table).
```

---

# CODING RULES

Ikuti standar Odoo 19.

Tidak boleh memodifikasi Odoo core.

Selalu gunakan:

```python
_inherit = 'hr.employee'   # Extend model yang sudah ada
```

Bukan:

```python
_name = 'hr.employee'      # Ini menimpa model, bukan extend
```

Hindari:

```
- Monkey patching
- Direct SQL (kecuali untuk reporting dengan alasan performa yang jelas)
- Memodifikasi file di folder odoo/addons/
```

Gunakan ORM Odoo:

```python
# Benar
employees = self.env['hr.employee'].search([('active', '=', True)])

# Hindari
self.env.cr.execute("SELECT * FROM hr_employee WHERE active = true")
```

---

# SECURITY RULES

Setiap modul wajib memiliki:

```
ir.model.access.csv     → Definisi hak akses ke model
Security Group          → Grup karyawan dan HR Admin
Record Rules            → Karyawan hanya bisa lihat data sendiri
Menu Access             → Menu hanya tampil sesuai role
```

Role yang digunakan:

```
group_hris_employee     → Karyawan
group_hris_hr_admin     → HR Admin
```

---

# VIEW RULES

Urutan pembuatan view:

```
1. Tree (List) View   → Tampilkan daftar data
2. Form View          → Tampilkan dan edit detail data
3. Search View        → Filter dan pencarian
4. Dashboard          → Dibuat terakhir, setelah semua data bekerja
```

Jangan membuat dashboard sebelum data dan workflow berfungsi dengan benar.

---

# TESTING RULES

Sebelum menandai task sebagai selesai, wajib melakukan:

```
1. Install Test     → Modul berhasil diinstal tanpa error
2. Upgrade Test     → Modul berhasil di-upgrade tanpa error
3. Security Test    → Hak akses bekerja sesuai role matrix
4. Access Test      → Karyawan tidak bisa akses data orang lain
5. Workflow Test    → Alur pengajuan dan approval berjalan benar
6. Reporting Test   → Laporan menghasilkan data yang benar
```

---

# DEBUGGING RULES

Jika terjadi error, AI wajib memeriksa secara berurutan:

```
1. Manifest (__manifest__.py)    → Dependency dan versi sudah benar?
2. Dependencies                  → Semua modul yang dibutuhkan sudah terinstal?
3. Security Access               → ir.model.access.csv sudah ada dan benar?
4. XML ID                        → Tidak ada duplicate XML ID?
5. View Inheritance              → inherit_id sudah benar?
6. ORM Constraint                → Validasi model sudah benar?
7. Python Log                    → Ada traceback di log?
8. Odoo Log                      → Ada error di server log Odoo?
```

Buat kode baru hanya setelah semua poin di atas sudah diperiksa.

---

# TASK ROADMAP

```
PHASE 01 — Foundation
  └── hris_base

PHASE 02 — Employee
  └── hris_employee

PHASE 03 — Attendance
  └── hris_attendance

PHASE 04 — Fingerprint
  └── hris_fingerprint

PHASE 05 — Leave (Izin, Cuti, Sakit)
  └── hris_timeoff

PHASE 06 — Payroll
  └── hris_payroll
  ⚠️  Audit modul Payroll Odoo wajib selesai sebelum phase ini dimulai

PHASE 07 — WhatsApp
  └── hris_whatsapp
  ⚠️  Provider WhatsApp wajib dipilih sebelum phase ini dimulai

PHASE 08 — Notification
  └── hris_notification

PHASE 09 — Portal
  └── hris_portal

PHASE 10 — Reporting
  └── hris_reporting
```

---

# TASK COMPLETION CHECKLIST

Sebelum menandai task sebagai selesai:

```
[ ] Business Flow sudah diperiksa sesuai BUSINESS_FLOW.md
[ ] Module Mapping sudah diperiksa sesuai MODULE_MAPPING.md
[ ] Data Dictionary sudah diperiksa sesuai DATA_DICTIONARY.md
[ ] API Contract sudah diperiksa sesuai API_CONTRACT.md
[ ] Security dan hak akses sudah diimplementasikan
[ ] Install test berhasil tanpa error
[ ] Upgrade test berhasil tanpa error
[ ] Access rights test sesuai role matrix
[ ] Reporting test menghasilkan data yang benar
[ ] Tidak ada error di log Odoo
```

---

# BLOCKERS YANG HARUS DISELESAIKAN

Sebelum development dilanjutkan, dua hal berikut wajib diselesaikan oleh Product Owner:

## Blocker 1 — Audit Modul Payroll

```
Status  : Belum audit
Dampak  : Phase 6 (hris_payroll) tidak bisa dimulai
Aksi    : Periksa instance Odoo 19 Community — apakah modul hr.payroll tersedia?
Deadline: Sebelum Phase 6 dimulai
```

## Blocker 2 — Pemilihan Provider WhatsApp

```
Status  : TBD
Dampak  : Phase 7 (hris_whatsapp) tidak bisa dimulai
Aksi    : Product Owner / Project Manager memilih dan mengkontrak provider WhatsApp
Deadline: Sebelum Phase 7 dimulai
Kandidat: Fonnte, Wablas, Zenziva, Twilio WhatsApp
```

---

# FINAL RULE

Jika fitur sudah ada di Odoo:

```
EXTEND IT — jangan buat ulang dari nol
```

Jika fitur tidak ada di Odoo:

```
CREATE CUSTOM MODULE — ikuti struktur modul yang sudah didefinisikan
```

Jika tidak yakin:

```
STOP
→ Baca MODULE_MAPPING.md
→ Jika masih tidak jelas, tanyakan ke Project Lead
→ Baru lanjutkan pengembangan
```