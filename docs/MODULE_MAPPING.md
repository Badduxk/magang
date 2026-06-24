# MODULE_MAPPING.md

# HRIS ODOO 19 - MODULE MAPPING & AUDIT

Version: 1.1
Status: Revised — Kontradiksi telah diselesaikan
Tanggal Revisi: Juni 2026

---

# CATATAN REVISI

Perubahan dari versi 1.0:

1. Ditambahkan klarifikasi Kiosk Mode: hanya digunakan sebagai fallback UI internal,
   bukan sebagai metode absensi alternatif. Sumber absensi tetap fingerprint.
2. Ditambahkan catatan bahwa WhatsApp provider masih TBD — modul hris_whatsapp
   didesain dengan interface abstrak agar mudah diganti saat provider dipilih.
3. Ditambahkan status audit Payroll yang masih pending.
4. Diseragamkan status Leave dengan DATA_DICTIONARY (menggunakan `pending`).
5. Diperjelas bahwa endpoint Leave dan Time Off di API menggunakan satu model yang sama.

---

# DESKRIPSI

Dokumen ini digunakan sebagai acuan pengembangan HRIS berbasis Odoo 19.

Tujuan dokumen ini:

* Mengidentifikasi modul bawaan Odoo yang dapat digunakan.
* Menentukan fitur yang cukup di-extend.
* Menentukan fitur yang harus dibuat custom.
* Menjadi acuan bersama Backend, Frontend, API, dan Integrasi.

---

# STATUS AUDIT MODUL

| Modul                   | Status          |
| ----------------------- | --------------- |
| Employees               | ✅ Selesai       |
| Attendances             | ✅ Selesai       |
| Time Off                | ✅ Selesai       |
| Payroll                 | ⏳ Belum Audit   |
| Website / Portal        | ⏳ Belum Audit   |
| Planning                | ⏳ Belum Audit   |
| Appraisal               | ⏳ Belum Audit   |
| Recruitment             | ⏳ Belum Audit   |
| Discuss                 | ⏳ Belum Audit   |
| WhatsApp Integration    | ⏳ Desain (Provider TBD) |
| Fingerprint Integration | ⏳ Desain        |

---

# ARSITEKTUR HRIS

## Modul Extend Odoo

Modul yang menggunakan fitur bawaan Odoo dan hanya dilakukan penyesuaian.

* Employees
* Attendances
* Time Off
* Payroll (jika tersedia di instance)
* Planning
* Appraisal
* Recruitment
* Website Portal

---

## Modul Custom

Modul yang harus dibuat dari awal oleh tim pengembang.

* hris_fingerprint
* hris_whatsapp
* hris_reports
* hris_portal (jika diperlukan)
* hris_payroll (jika modul payroll Odoo tidak tersedia)

---

# A. EMPLOYEES

## Modul Odoo yang Digunakan

### Extend Module

* hr.employee
* hr.department
* resource.calendar
* hr.work.location

---

## Mapping Kebutuhan HRIS

| Kebutuhan HRIS | Modul Odoo        | Status |
| -------------- | ----------------- | ------ |
| Data Karyawan  | hr.employee       | Extend |
| Departemen     | hr.department     | Extend |
| Jadwal Kerja   | resource.calendar | Extend |
| Lokasi Kerja   | hr.work.location  | Extend |

---

## Fungsi Modul

### hr.employee

Extend untuk menyimpan field tambahan:

* NIK (Nomor Induk Karyawan)
* Nomor NPWP
* Nama bank dan nomor rekening
* employee_type (tetap / freelance)
* Tanggal masuk kerja

Field standar yang sudah ada di Odoo:

* Nama lengkap
* Email
* Nomor HP
* Jabatan
* Departemen
* Manager
* Status karyawan

---

### hr.department

Extend minimal — field bawaan Odoo sudah mencukupi:

* Nama departemen
* Manager departemen
* Struktur organisasi

---

### resource.calendar

Digunakan untuk mendefinisikan:

* Jam masuk dan jam pulang
* Shift kerja
* Dasar perhitungan jam kerja harian (8 jam)
* Dasar perhitungan lembur (lebih dari 8 jam)
* Dasar perhitungan payroll

---

### hr.work.location

Digunakan untuk mendefinisikan lokasi kerja:

* Kantor pusat
* Kantor cabang
* Lokasi proyek
* WFH (Work From Home)
* WFO (Work From Office)

---

## Kesimpulan

Tidak perlu membuat modul karyawan baru.
Cukup extend modul yang sudah ada:

* hr.employee
* hr.department
* resource.calendar
* hr.work.location

---

# B. ATTENDANCES

## Modul Odoo yang Digunakan

### Extend Module

* hr.attendance
* Attendances Reporting
* Overtime Rulesets

> **Catatan Kiosk Mode:**
> Kiosk Mode (barcode, RFID, manual identification) adalah fitur bawaan Odoo yang tersedia
> di modul Attendances. Namun, dalam HRIS ini, Kiosk Mode **tidak digunakan sebagai metode
> absensi karyawan**. Absensi hanya melalui mesin fingerprint yang diintegrasikan via
> modul custom `hris_fingerprint`.
>
> Kiosk Mode dapat dinonaktifkan di konfigurasi, atau dibiarkan tersedia namun hanya
> digunakan oleh HR Admin untuk keperluan koreksi data internal — bukan untuk absensi harian.

---

## Mapping Kebutuhan

| Kebutuhan HRIS          | Odoo                  | Status  |
| ----------------------- | --------------------- | ------- |
| Absensi Masuk           | hr.attendance         | Extend  |
| Absensi Pulang          | hr.attendance         | Extend  |
| Durasi Kerja            | hr.attendance         | Extend  |
| Perhitungan Jam Kerja   | hr.attendance         | Extend  |
| Lembur Otomatis         | Overtime Rulesets     | Extend  |
| Rekap Absensi           | Attendances Reporting | Extend  |
| Fingerprint Integration | Tidak Ada di Odoo     | Custom  |
| WhatsApp Rekap          | Tidak Ada di Odoo     | Custom  |
| Koreksi Absensi Manual  | Tidak Ada di Odoo     | Custom  |
| Kiosk Mode              | Ada di Odoo           | Nonaktif|
| Alasan Tidak Hadir      | Belum Audit           | Pending |

---

## Fitur Bawaan Odoo

### hr.attendance

Fitur yang sudah tersedia:

* Check In
* Check Out
* Worked Hours (total jam kerja)
* Extra Hours (kelebihan jam = lembur)

---

### Attendances Reporting

Fitur yang sudah tersedia:

* Rekap harian
* Rekap bulanan
* Grafik kehadiran
* Pivot report
* Export data

---

### Overtime Rulesets

Fitur yang sudah tersedia:

* Aturan lembur (threshold jam kerja)
* Rate lembur (dapat dikonfigurasi)
* Perhitungan lembur otomatis

---

## Modul Custom

### hris_fingerprint

Fungsi utama:

* Integrasi mesin fingerprint (Magic Fingerprint)
* Import dan parsing log fingerprint
* Sinkronisasi real-time ke hr.attendance
* Mapping fingerprint ID ke hr.employee
* Fallback: simpan offline jika koneksi putus, sync saat online kembali

---

### hris_whatsapp (bagian attendance)

Fungsi untuk absensi:

* Notifikasi karyawan saat absensi berhasil tercatat
* Rekap harian ke pimpinan
* Rekap bulanan ke pimpinan
* Notifikasi HR Admin jika sinkronisasi fingerprint gagal

---

## Kesimpulan

Tidak perlu membuat sistem absensi baru.
Cukup extend hr.attendance + Overtime Rulesets untuk logika bisnis.
Tambahkan modul custom hris_fingerprint untuk integrasi mesin.

---

# C. TIME OFF (IZIN & CUTI)

## Modul Odoo yang Digunakan

### Extend Module

* hr.leave
* hr.leave.type
* My Time Off
* My Allocations
* Overview Dashboard
* Management Time Off
* Reporting
* Configuration

---

## Mapping Kebutuhan

| Kebutuhan HRIS        | Odoo            | Status  |
| --------------------- | --------------- | ------- |
| Izin                  | hr.leave        | Extend  |
| Cuti                  | hr.leave        | Extend  |
| Sakit                 | hr.leave        | Extend  |
| Approval              | hr.leave        | Extend  |
| Reject                | hr.leave        | Extend  |
| Cancel                | hr.leave        | Extend  |
| Kuota Cuti            | My Allocations  | Extend  |
| Rekap Izin            | Reporting       | Extend  |
| Rekap Cuti            | Reporting       | Extend  |
| Hari Libur Nasional   | Public Holidays | Extend  |
| Notifikasi WhatsApp   | Tidak Ada       | Custom  |
| Validasi Tipe Karyawan| Tidak Ada       | Custom  |
| Lampiran Surat Dokter | hr.leave        | Extend  |

---

## Struktur Model

Izin, cuti, dan sakit menggunakan **satu model** yang sama: `hr.leave`.
Pembeda antara ketiganya adalah `holiday_status_id` (Leave Type di Odoo).

Konfigurasi Leave Type yang perlu dibuat:

| Leave Type | Kode     | Lampiran  | Potong Kuota | Berlaku Untuk   |
| ---------- | -------- | --------- | ------------ | --------------- |
| Izin       | IZIN     | Opsional  | Ya           | Semua karyawan  |
| Cuti       | CUTI     | Tidak     | Ya           | Tetap saja      |
| Sakit      | SAKIT    | Wajib     | Tidak        | Semua karyawan  |

> **Catatan untuk Developer:**
> API endpoint `/api/v1/leaves` (izin) dan `/api/v1/time-off` (cuti) keduanya
> menggunakan model `hr.leave` yang sama di backend.
> Perbedaan hanya pada `holiday_status_id` yang dikirim dalam request.
> Controller API cukup satu, dengan routing berdasarkan path yang berbeda
> untuk memudahkan pemahaman frontend.

---

## Mapping Status

Penyeragaman status antara HRIS, Odoo, dan API:

| Status HRIS (internal) | Status Odoo    | Tampil di API/UI sebagai |
| ---------------------- | -------------- | ------------------------ |
| pending                | to_approve     | Menunggu Persetujuan     |
| approved               | approved       | Disetujui                |
| rejected               | refused        | Ditolak                  |
| cancelled              | cancel         | Dibatalkan               |

> **Penting:** Status awal selalu `pending` (to_approve di Odoo).
> Gunakan nilai `pending` di database dan API response.
> Jangan gunakan `on_proses` atau `waiting` — istilah tersebut tidak baku di sistem ini.

---

## Workflow Approval

Workflow approval bawaan Odoo sudah memenuhi kebutuhan HRIS.
Satu level approval: karyawan mengajukan → HR Admin menyetujui/menolak.

Tidak perlu membuat workflow baru.

---

## Validasi Custom yang Perlu Ditambahkan

Karena keterbatasan bawaan Odoo, perlu dibuat validasi tambahan via Python:

```python
# Validasi 1: Freelance tidak boleh mengajukan cuti
if leave_type == 'CUTI' and employee.employee_type == 'freelance':
    raise ValidationError("Tipe karyawan freelance tidak memiliki hak cuti.")

# Validasi 2: Sakit wajib lampirkan surat dokter
if leave_type == 'SAKIT' and not attachment:
    raise ValidationError("Surat dokter wajib dilampirkan untuk pengajuan sakit.")

# Validasi 3: Kuota cuti tidak boleh minus
if leave_type in ['IZIN', 'CUTI'] and leave_balance.remaining_quota < total_days:
    raise ValidationError("Sisa kuota cuti tidak mencukupi.")
```

---

## Integrasi WhatsApp

Notifikasi yang dikirim otomatis saat event terjadi:

* Pengajuan baru diterima → notifikasi ke HR Admin
* Pengajuan disetujui → notifikasi ke karyawan
* Pengajuan ditolak → notifikasi ke karyawan

---

# D. PAYROLL

## Status Audit

**BELUM DIAUDIT** — Menunggu pemeriksaan instance Odoo 19.

---

## Catatan

Pada instance Odoo 19 Community saat ini belum dikonfirmasi ketersediaan modul Payroll.

Tim perlu memastikan:

* Apakah Odoo 19 Community menyertakan modul hr.payroll?
* Jika tidak ada: gunakan modul payroll dari pihak ketiga yang kompatibel.
* Jika tidak ada yang sesuai: buat modul custom hris_payroll.

---

## Kebutuhan Payroll yang Wajib Terpenuhi

| Kebutuhan        | Prioritas | Status        |
| ---------------- | --------- | ------------- |
| Generate Payroll | Tinggi    | Pending Audit |
| Slip Gaji PDF    | Tinggi    | Pending Audit |
| PPh21 Otomatis   | Tinggi    | Pending Audit |
| Potongan Alpha   | Tinggi    | Pending Audit |
| Lembur ke Payroll| Tinggi    | Pending Audit |
| Tunjangan        | Sedang    | Pending Audit |
| BPJS             | Sedang    | Pending Audit |
| THR              | Sedang    | Pending Audit |

---

# E. WEBSITE / PORTAL

## Status Audit

**BELUM DIAUDIT**

---

## Kebutuhan Portal Karyawan

Fitur yang harus tersedia di Employee Portal:

* Login dengan username dan password
* Dashboard ringkasan karyawan
* Lihat dan cari riwayat absensi
* Ajukan izin / cuti / sakit
* Lihat status pengajuan
* Download slip gaji
* Update profil sendiri

Batasan:

* Karyawan hanya bisa melihat data miliknya sendiri
* Tidak ada akses ke data karyawan lain

---

## Kandidat Modul Odoo

* website
* portal
* qweb (template)

---

# F. WHATSAPP INTEGRATION

## Modul Custom: hris_whatsapp

---

## Desain Arsitektur

Modul `hris_whatsapp` dirancang dengan **interface abstrak (adapter pattern)**.
Tujuannya agar provider WhatsApp bisa diganti tanpa mengubah kode bisnis.

```
Business Logic (hris_whatsapp)
    ↓
WhatsApp Adapter Interface
    ↓
Provider Konkret (Fonnte / Wablas / Twilio / dll)
```

> **Status Provider: TBD (To Be Determined)**
>
> Provider WhatsApp belum dipilih saat dokumen ini dibuat.
> Keputusan pemilihan provider harus dilakukan sebelum fase implementasi hris_whatsapp.
>
> Kriteria yang harus dipenuhi provider:
> * Mendukung pengiriman pesan teks biasa
> * Mendukung template message
> * Memiliki API yang stabil dan terdokumentasi
> * Mendukung pengiriman ke banyak nomor (bulk)
> * Harga terjangkau untuk skala perusahaan kecil-menengah
>
> Kandidat provider yang bisa dievaluasi:
> * Fonnte (lokal, murah)
> * Wablas (lokal)
> * Zenziva (lokal)
> * Twilio WhatsApp (internasional)

---

## Notifikasi Karyawan

Pesan yang dikirim ke karyawan:

* Absensi masuk berhasil tercatat
* Pengajuan izin/cuti/sakit berhasil dikirim (pending)
* Izin/cuti/sakit disetujui
* Izin/cuti/sakit ditolak
* Slip gaji tersedia dan bisa diunduh

---

## Notifikasi HR Admin

Pesan yang dikirim ke HR Admin:

* Ada pengajuan izin/cuti/sakit baru
* Sinkronisasi fingerprint gagal
* Error saat proses generate payroll

---

## Laporan ke Pimpinan

Pesan yang dikirim ke pimpinan:

* Rekap absensi harian (otomatis setiap akhir hari kerja)
* Rekap absensi bulanan (otomatis setiap awal bulan)
* Daftar karyawan terlambat
* Daftar karyawan tidak hadir (alpha)
* Ringkasan payroll bulanan

---

# G. FINGERPRINT INTEGRATION

## Modul Custom: hris_fingerprint

---

## Spesifikasi Mesin

* Merek/tipe: Magic Fingerprint
* Jumlah mesin: 1 unit
* Mode sinkronisasi: Real-time (jika online)
* Fallback: Simpan data offline di mesin, sync otomatis saat koneksi tersambung kembali

---

## Fitur Modul

* Registrasi dan pengelolaan mesin fingerprint
* Sinkronisasi data karyawan dari Odoo ke mesin
* Import log fingerprint dari mesin ke sistem
* Mapping fingerprint ID ke hr.employee
* Generate record hr.attendance dari log fingerprint
* Notifikasi WhatsApp ke HR Admin jika sinkronisasi gagal

---

## Alur Proses

```
Karyawan scan fingerprint di mesin
        ↓
Mesin Fingerprint menyimpan log scan
        ↓
hris_fingerprint tarik log via API atau koneksi langsung
        ↓
Mapping fingerprint ID → employee_id
        ↓
Generate record di hr.attendance (check_in / check_out)
        ↓
Hitung worked_hours dan overtime_hours
        ↓
Update attendance_status
        ↓
Kirim notifikasi WhatsApp ke karyawan
        ↓
Data siap untuk Reporting dan Payroll
```

---

# DAFTAR MODUL CUSTOM FINAL

## hris_fingerprint

Integrasi mesin fingerprint Magic.
Menghasilkan data hr.attendance dari log fingerprint.

---

## hris_whatsapp

Integrasi WhatsApp Gateway.
Dirancang dengan adapter pattern agar provider bisa diganti.
**Provider belum dipilih — wajib ditentukan sebelum implementasi.**

---

## hris_reports

Laporan khusus perusahaan.

Fitur:

* Rekap absensi harian
* Rekap absensi bulanan
* Rekap ketidakhadiran (alpha)
* Rekap lembur
* Rekap pengajuan izin/cuti/sakit

---

# KESIMPULAN AUDIT SAAT INI

## Modul yang Di-extend

* hr.employee
* hr.department
* resource.calendar
* hr.work.location
* hr.attendance
* Attendances Reporting
* Overtime Rulesets
* hr.leave
* hr.leave.type
* My Time Off
* My Allocations
* Time Off Reporting

---

## Modul Custom yang Dibuat

* hris_fingerprint
* hris_whatsapp
* hris_reports

---

## Pending Audit

* Payroll (prioritas tinggi — harus diaudit sebelum Phase 6)
* Website / Portal
* Planning
* Recruitment
* Appraisal
* Discuss

---

## Yang Dinonaktifkan

* Kiosk Mode — fitur absensi manual dari Odoo dinonaktifkan karena tidak sesuai
  dengan aturan bisnis (absensi hanya via fingerprint)

---

Versi Dokumen: 1.1
Tanggal Audit Terakhir: Juni 2026
Platform: Odoo 19 Community