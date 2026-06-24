# DATA_DICTIONARY.md

# HRIS ODOO 19

## DATA DICTIONARY

Version: 1.1
Status: Revised — Kontradiksi telah diselesaikan
Tanggal Revisi: Juni 2026

---

# CATATAN REVISI

Perubahan dari versi 1.0:

1. Field `attachment` di Leave Request diubah dari Required=Yes menjadi kondisional:
   wajib hanya untuk leave_type=sakit, opsional untuk izin, tidak diperlukan untuk cuti.
2. Ditambahkan constraint `employee_type` pada Leave Balance — hanya karyawan tetap.
3. Ditambahkan kolom `formula` pada tabel Overtime untuk menjelaskan cara hitung nominal.
4. Ditambahkan Business Rule untuk alpha_deduction agar jelas cara hitungnya.
5. Diseragamkan nilai `approval_status` initial: menggunakan `pending` secara konsisten.
6. Dihapus referensi email dari entity Payslip — hanya WhatsApp.
7. Ditambahkan constraint employee_type pada Leave Request.

---

# TUJUAN

Dokumen ini menjadi standar seluruh proyek HRIS.

Digunakan oleh:

* Backend Developer
* Frontend Developer
* Mobile Developer
* API Developer
* QA Tester
* AI Assistant (Copilot, Claude Code, Cursor, Antigravity)

Seluruh penamaan field wajib mengikuti dokumen ini.

---

# NAMING CONVENTION

## Format Penamaan

Gunakan:

```text
snake_case
```

Contoh:

```text
employee_id
employee_name
employee_type
attendance_status
created_at
updated_at
```

---

## Primary Key

Format:

```text
<entity>_id
```

Contoh:

```text
employee_id
department_id
attendance_id
leave_id
payroll_id
```

---

## Foreign Key

Format:

```text
<entity>_id
```

Contoh:

```text
employee_id
department_id
payroll_id
```

---

## Datetime

Format:

```text
YYYY-MM-DD HH:mm:ss
```

Contoh:

```text
2026-06-24 08:00:00
```

---

# MASTER DATA

---

# EMPLOYEE

## Entity

Employee

## Description

Menyimpan seluruh data karyawan aktif maupun tidak aktif.

---

| Field               | Type      | Required | Description                         |
| ------------------- | --------- | :------: | ----------------------------------- |
| employee_id         | Integer   | Yes      | ID unik karyawan (primary key)      |
| employee_code       | String    | Yes      | Kode karyawan (format: EMP-XXXX)    |
| nik                 | String    | Yes      | Nomor Induk Karyawan (16 digit)     |
| full_name           | String    | Yes      | Nama lengkap karyawan               |
| email               | String    | Yes      | Email karyawan (untuk akun sistem)  |
| phone_number        | String    | Yes      | Nomor HP aktif (format WhatsApp)    |
| photo               | Binary    | Yes      | Foto karyawan                       |
| employee_type       | Selection | Yes      | Jenis karyawan (lihat nilai di bawah)|
| department_id       | Integer   | Yes      | FK ke tabel Department              |
| job_position        | String    | Yes      | Jabatan karyawan                    |
| manager_id          | Integer   | No       | FK ke employee_id atasan langsung   |
| npwp_number         | String    | Yes      | Nomor NPWP untuk keperluan PPh21    |
| bank_name           | String    | Yes      | Nama bank untuk transfer gaji       |
| bank_account_number | String    | Yes      | Nomor rekening bank                 |
| join_date           | Date      | Yes      | Tanggal pertama masuk kerja         |
| status              | Selection | Yes      | Status karyawan (lihat nilai di bawah)|
| created_at          | Datetime  | Yes      | Tanggal record dibuat               |
| updated_at          | Datetime  | Yes      | Tanggal record terakhir diubah      |

---

## Nilai employee_type

```text
tetap       → Karyawan Tetap: mendapat izin, cuti, sakit, payroll
freelance   → Karyawan Freelance: mendapat izin, sakit, payroll (tidak ada cuti)
```

---

## Nilai status

```text
active      → Karyawan sedang aktif bekerja
inactive    → Karyawan nonaktif sementara
resigned    → Karyawan sudah keluar/berhenti
```

---

# DEPARTMENT

## Entity

Department

## Description

Menyimpan data departemen perusahaan.

---

| Field           | Type     | Required | Description                      |
| --------------- | -------- | :------: | -------------------------------- |
| department_id   | Integer  | Yes      | ID unik departemen (primary key) |
| department_code | String   | Yes      | Kode departemen (format: DEPT-XX)|
| department_name | String   | Yes      | Nama departemen                  |
| description     | Text     | No       | Deskripsi atau keterangan        |
| created_at      | Datetime | Yes      | Tanggal record dibuat            |
| updated_at      | Datetime | Yes      | Tanggal record terakhir diubah   |

---

# WORK LOCATION

## Entity

Work Location

## Description

Menyimpan data lokasi kerja (kantor, cabang, proyek, dll).

---

| Field         | Type      | Required | Description                         |
| ------------- | --------- | :------: | ----------------------------------- |
| location_id   | Integer   | Yes      | ID unik lokasi (primary key)        |
| location_name | String    | Yes      | Nama lokasi kerja                   |
| address       | Text      | Yes      | Alamat lengkap lokasi               |
| city          | String    | Yes      | Kota                                |
| province      | String    | Yes      | Provinsi                            |
| postal_code   | String    | No       | Kode pos                            |
| status        | Selection | Yes      | Status lokasi (lihat nilai di bawah)|
| created_at    | Datetime  | Yes      | Tanggal record dibuat               |

---

## Nilai status

```text
active      → Lokasi aktif digunakan
inactive    → Lokasi tidak aktif
```

---

# TRANSACTION DATA

---

# ATTENDANCE

## Entity

Attendance

## Description

Data absensi harian yang berasal dari sinkronisasi mesin fingerprint.
Tidak ada input manual dari user. Seluruh record dibuat otomatis oleh sistem
saat fingerprint disinkronisasi.

---

| Field             | Type      | Required | Description                                  |
| ----------------- | --------- | :------: | -------------------------------------------- |
| attendance_id     | Integer   | Yes      | ID unik absensi (primary key)                |
| employee_id       | Integer   | Yes      | FK ke tabel Employee                         |
| attendance_date   | Date      | Yes      | Tanggal absensi (YYYY-MM-DD)                 |
| check_in          | Datetime  | Yes      | Waktu masuk dari fingerprint pertama         |
| check_out         | Datetime  | No       | Waktu pulang dari fingerprint terakhir       |
| worked_hours      | Decimal   | Yes      | Total jam kerja = check_out - check_in       |
| overtime_hours    | Decimal   | No       | Jam lembur = worked_hours - 8 (jika > 8)    |
| attendance_status | Selection | Yes      | Status kehadiran (lihat nilai di bawah)      |
| source            | Selection | Yes      | Sumber data (lihat nilai di bawah)           |
| created_at        | Datetime  | Yes      | Tanggal record dibuat                        |
| updated_at        | Datetime  | Yes      | Tanggal record terakhir diubah               |

---

## Nilai attendance_status

```text
hadir   → Karyawan hadir (ada check_in dari fingerprint)
izin    → Karyawan izin (ada leave_request dengan leave_type=izin yang approved)
cuti    → Karyawan cuti (ada leave_request dengan leave_type=cuti yang approved)
sakit   → Karyawan sakit (ada leave_request dengan leave_type=sakit yang approved)
alpha   → Tidak hadir tanpa keterangan apapun (otomatis oleh sistem)
```

## Nilai source

```text
fingerprint → Data berasal dari sinkronisasi mesin fingerprint (sumber utama)
manual      → Data dikoreksi secara manual oleh HR Admin
system      → Data dibuat otomatis oleh sistem (misal: karyawan izin/cuti approved)
```

## Aturan Perhitungan

```text
overtime_hours = 0                    jika worked_hours <= 8
overtime_hours = worked_hours - 8     jika worked_hours > 8

Jika tidak ada record attendance, izin, cuti, atau sakit pada hari kerja:
→ sistem membuat record dengan attendance_status = alpha secara otomatis.
```

---

# OVERTIME

## Entity

Overtime

## Description

Lembur dihitung otomatis oleh sistem berdasarkan data attendance.
Karyawan tidak mengajukan lembur. Tidak ada approval lembur.

---

| Field           | Type     | Required | Description                                       |
| --------------- | -------- | :------: | ------------------------------------------------- |
| overtime_id     | Integer  | Yes      | ID unik lembur (primary key)                      |
| employee_id     | Integer  | Yes      | FK ke tabel Employee                              |
| attendance_id   | Integer  | Yes      | FK ke tabel Attendance (sumber data lembur)       |
| overtime_date   | Date     | Yes      | Tanggal lembur                                    |
| overtime_hours  | Decimal  | Yes      | Total jam lembur pada hari tersebut               |
| overtime_amount | Decimal  | No       | Nominal rupiah lembur (dihitung saat generate payroll)|
| created_at      | Datetime | Yes      | Tanggal record dibuat                             |

---

## Aturan Perhitungan overtime_amount

```text
overtime_amount = overtime_hours × (basic_salary / 173)

Keterangan:
- 173 adalah standar jam kerja bulanan (8 jam × 21.75 hari kerja rata-rata)
- basic_salary diambil dari kontrak karyawan yang berlaku
- overtime_amount diisi saat proses generate payroll dijalankan, bukan real-time
- Sebelum payroll di-generate, overtime_amount = NULL / kosong
```

---

# LEAVE REQUEST

## Entity

Leave Request

## Description

Menyimpan semua pengajuan karyawan: izin, cuti, dan sakit.
Satu tabel untuk ketiga jenis pengajuan, dibedakan dengan field `leave_type`.

---

| Field           | Type      | Required   | Description                                          |
| --------------- | --------- | :--------: | ---------------------------------------------------- |
| leave_id        | Integer   | Yes        | ID unik pengajuan (primary key)                      |
| employee_id     | Integer   | Yes        | FK ke tabel Employee                                 |
| leave_type      | Selection | Yes        | Jenis pengajuan (lihat nilai di bawah)               |
| start_date      | Date      | Yes        | Tanggal mulai                                        |
| end_date        | Date      | Yes        | Tanggal selesai                                      |
| total_days      | Integer   | Yes        | Jumlah hari = end_date - start_date + 1              |
| reason          | Text      | Yes        | Alasan pengajuan                                     |
| attachment      | Binary    | Kondisional| Lihat aturan lampiran di bawah                       |
| approval_status | Selection | Yes        | Status approval (lihat nilai di bawah)               |
| approved_by     | Integer   | No         | FK ke employee_id HR Admin yang menyetujui           |
| approved_at     | Datetime  | No         | Waktu approval dilakukan                             |
| created_at      | Datetime  | Yes        | Tanggal pengajuan dibuat                             |

---

## Nilai leave_type

```text
izin    → Izin tidak masuk (potongan kuota cuti, lampiran opsional)
cuti    → Cuti tahunan (potongan kuota cuti, tanpa lampiran, khusus karyawan tetap)
sakit   → Sakit (tidak potong kuota cuti, surat dokter WAJIB dilampirkan)
```

## Aturan Lampiran (attachment)

```text
leave_type = izin   → attachment OPSIONAL  (boleh diisi, boleh kosong)
leave_type = cuti   → attachment TIDAK DIPERLUKAN (selalu kosong)
leave_type = sakit  → attachment WAJIB (harus diisi, tanpa lampiran sistem tolak pengajuan)
```

## Nilai approval_status

```text
pending     → Pengajuan baru, menunggu keputusan HR Admin (status awal selalu pending)
approved    → Disetujui oleh HR Admin
rejected    → Ditolak oleh HR Admin
cancelled   → Dibatalkan oleh karyawan sebelum diproses
```

## Constraint Validasi

```text
1. Jika leave_type = cuti DAN employee.employee_type = freelance
   → Sistem menolak pengajuan dengan error: "Freelance tidak memiliki hak cuti"

2. Jika leave_type = sakit DAN attachment = NULL
   → Sistem menolak pengajuan dengan error: "Surat dokter wajib dilampirkan"

3. Jika leave_type = cuti DAN leave_balance.remaining_quota = 0
   → Sistem menolak pengajuan dengan error: "Kuota cuti habis"
```

---

# LEAVE BALANCE

## Entity

Leave Balance

## Description

Menyimpan saldo kuota cuti karyawan tetap.
Hanya karyawan tetap yang memiliki record di tabel ini.
Karyawan freelance tidak memiliki kuota cuti dan tidak ada record di tabel ini.

---

| Field           | Type     | Required | Description                                     |
| --------------- | -------- | :------: | ----------------------------------------------- |
| balance_id      | Integer  | Yes      | ID unik saldo (primary key)                     |
| employee_id     | Integer  | Yes      | FK ke tabel Employee (hanya employee_type=tetap)|
| year            | Integer  | Yes      | Tahun berlaku kuota cuti                        |
| total_quota     | Integer  | Yes      | Total kuota cuti dalam setahun (dalam hari)     |
| used_quota      | Integer  | Yes      | Kuota yang sudah dipakai (cuti + izin)          |
| remaining_quota | Integer  | Yes      | Sisa kuota = total_quota - used_quota           |
| updated_at      | Datetime | Yes      | Tanggal terakhir diubah                         |

---

## Aturan

```text
- Hanya dibuat untuk employee_type = tetap
- Kuota berkurang saat pengajuan izin atau cuti disetujui (approved)
- Kuota dikembalikan saat pengajuan dibatalkan (cancelled) atau ditolak (rejected)
- remaining_quota tidak boleh kurang dari 0
```

---

# MEDICAL CERTIFICATE

## Entity

Medical Certificate

## Description

Menyimpan referensi surat dokter yang dilampirkan pada pengajuan sakit.
Entity ini terpisah dari Leave Request untuk memudahkan pengelolaan dokumen medis.
Setiap pengajuan sakit (leave_type=sakit) wajib memiliki satu record Medical Certificate.

---

| Field           | Type      | Required | Description                                         |
| --------------- | --------- | :------: | --------------------------------------------------- |
| certificate_id  | Integer   | Yes      | ID unik surat dokter (primary key)                  |
| employee_id     | Integer   | Yes      | FK ke tabel Employee                                |
| leave_id        | Integer   | Yes      | FK ke tabel Leave Request (leave_type harus = sakit)|
| file_attachment | Binary    | Yes      | File surat dokter atau bukti medis                  |
| approval_status | Selection | Yes      | Status verifikasi (lihat nilai di bawah)            |
| approved_by     | Integer   | No       | FK ke employee_id HR Admin                          |
| approved_at     | Datetime  | No       | Waktu verifikasi dilakukan                          |

---

## Nilai approval_status

```text
pending     → Belum diverifikasi HR Admin (status awal)
approved    → Surat dokter diverifikasi dan disetujui
rejected    → Surat dokter ditolak (tidak valid atau tidak terbaca)
```

## Hubungan dengan Leave Request

```text
- Satu Leave Request (sakit) memiliki tepat satu Medical Certificate
- file_attachment di Medical Certificate adalah file yang sebenarnya
- Field attachment di Leave Request untuk leave_type=sakit merujuk ke Medical Certificate
- Tidak ada duplikasi file: file disimpan di Medical Certificate, bukan di keduanya
```

---

# PAYROLL

## Entity

Payroll

## Description

Menyimpan data payroll bulanan per karyawan.
Payroll di-generate oleh HR Admin setiap bulan, paling lambat tanggal 28.

---

| Field            | Type      | Required | Description                                         |
| ---------------- | --------- | :------: | --------------------------------------------------- |
| payroll_id       | Integer   | Yes      | ID unik payroll (primary key)                       |
| employee_id      | Integer   | Yes      | FK ke tabel Employee                                |
| payroll_month    | Integer   | Yes      | Bulan payroll (1-12)                                |
| payroll_year     | Integer   | Yes      | Tahun payroll                                       |
| basic_salary     | Decimal   | Yes      | Gaji pokok dari kontrak karyawan                    |
| overtime_amount  | Decimal   | No       | Total nominal lembur bulan tersebut                 |
| allowance_amount | Decimal   | No       | Total tunjangan (transport, makan, dll)             |
| alpha_deduction  | Decimal   | No       | Potongan karena ketidakhadiran tanpa keterangan     |
| pph21_amount     | Decimal   | No       | Pajak penghasilan PPh21                             |
| total_salary     | Decimal   | Yes      | Gaji akhir yang diterima karyawan                   |
| payroll_status   | Selection | Yes      | Status payroll (lihat nilai di bawah)               |
| generated_at     | Datetime  | No       | Waktu generate payroll dilakukan                    |

---

## Nilai payroll_status

```text
draft       → Payroll sedang disiapkan, belum final
generated   → Payroll sudah di-generate, siap diproses pembayaran
paid        → Gaji sudah dibayarkan ke karyawan
cancelled   → Payroll dibatalkan
```

## Rumus Perhitungan total_salary

```text
total_salary = basic_salary
             + overtime_amount
             + allowance_amount
             - alpha_deduction
             - pph21_amount
```

## Rumus Perhitungan alpha_deduction

```text
alpha_deduction = jumlah_hari_alpha × (basic_salary / jumlah_hari_kerja_bulan_tersebut)

Keterangan:
- jumlah_hari_alpha: total hari kerja dengan attendance_status = alpha pada bulan tersebut
- jumlah_hari_kerja_bulan_tersebut: total hari kerja aktif pada bulan tersebut
  (tidak termasuk hari libur nasional dan weekend)
- Potongan alpha bersifat prorata dari gaji pokok
```

## Rumus Perhitungan pph21_amount

```text
pph21_amount dihitung berdasarkan:
1. Penghasilan bruto bulanan = basic_salary + overtime_amount + allowance_amount
2. Penghasilan bruto tahunan = penghasilan bruto bulanan × 12
3. Penghasilan Kena Pajak (PKP) = penghasilan bruto tahunan - PTKP
4. PPh21 tahunan = PKP × tarif progresif (sesuai UU PPh Pasal 17)
5. PPh21 bulanan = PPh21 tahunan / 12

Tarif progresif PPh21:
- PKP ≤ 60 juta/tahun       → 5%
- PKP 60–250 juta/tahun     → 15%
- PKP 250–500 juta/tahun    → 25%
- PKP 500 juta–5 miliar/tahun → 30%
- PKP > 5 miliar/tahun      → 35%

PTKP (Penghasilan Tidak Kena Pajak) dikonfigurasi di sistem sesuai status pernikahan.
Nilai PTKP wajib diinput oleh HR Admin di master data karyawan.
```

---

# PAYSLIP

## Entity

Payslip

## Description

Menyimpan data slip gaji yang di-generate dari payroll.
Slip gaji tersedia dalam format PDF dan dapat diunduh oleh karyawan.
Notifikasi slip gaji dikirim via WhatsApp — tidak ada pengiriman via email.

---

| Field         | Type     | Required | Description                                    |
| ------------- | -------- | :------: | ---------------------------------------------- |
| payslip_id    | Integer  | Yes      | ID unik slip gaji (primary key)                |
| payroll_id    | Integer  | Yes      | FK ke tabel Payroll                            |
| employee_id   | Integer  | Yes      | FK ke tabel Employee                           |
| pdf_file      | String   | Yes      | Path atau URL file PDF slip gaji               |
| whatsapp_sent | Boolean  | Yes      | Status pengiriman notifikasi WhatsApp          |
| sent_at       | Datetime | No       | Waktu notifikasi WhatsApp dikirim              |
| created_at    | Datetime | Yes      | Tanggal slip gaji dibuat                       |

---

## Catatan

```text
- Tidak ada field email_sent karena sistem tidak menggunakan email
- Notifikasi WhatsApp hanya memberitahu bahwa slip gaji tersedia
- Karyawan mengunduh slip gaji secara mandiri melalui portal atau aplikasi
- HR Admin juga dapat mengunduh slip gaji semua karyawan
```

---

# FINGERPRINT DEVICE

## Entity

Fingerprint Device

## Description

Menyimpan data mesin fingerprint yang terdaftar di sistem.

---

| Field         | Type      | Required | Description                              |
| ------------- | --------- | :------: | ---------------------------------------- |
| device_id     | Integer   | Yes      | ID unik device (primary key)             |
| device_name   | String    | Yes      | Nama atau label mesin fingerprint        |
| device_type   | String    | Yes      | Tipe atau model mesin                    |
| serial_number | String    | Yes      | Serial number mesin                      |
| ip_address    | String    | No       | IP address mesin (untuk koneksi jaringan)|
| status        | Selection | Yes      | Status mesin (lihat nilai di bawah)      |
| last_sync_at  | Datetime  | No       | Waktu terakhir sinkronisasi berhasil     |

---

## Nilai status

```text
online      → Mesin aktif dan terhubung
offline     → Mesin tidak terhubung atau tidak responsif
maintenance → Mesin sedang dalam perbaikan
```

---

# FINGERPRINT LOG

## Entity

Fingerprint Log

## Description

Menyimpan setiap scan dari mesin fingerprint sebelum diproses menjadi Attendance.
Log ini berfungsi sebagai raw data sebelum validasi dan mapping ke karyawan.

---

| Field       | Type      | Required | Description                               |
| ----------- | --------- | :------: | ----------------------------------------- |
| log_id      | Integer   | Yes      | ID unik log (primary key)                 |
| employee_id | Integer   | Yes      | FK ke tabel Employee (hasil mapping)      |
| device_id   | Integer   | Yes      | FK ke tabel Fingerprint Device            |
| scan_time   | Datetime  | Yes      | Waktu scan dari mesin fingerprint         |
| sync_status | Selection | Yes      | Status sinkronisasi (lihat nilai di bawah)|

---

## Nilai sync_status

```text
pending → Log diterima, belum diproses ke Attendance
success → Log sudah diproses dan attendance telah dibuat
failed  → Log gagal diproses (biasanya karena mapping employee tidak ditemukan)
```

---

# WHATSAPP NOTIFICATION

## Entity

WhatsApp Notification

## Description

Menyimpan log setiap notifikasi WhatsApp yang dikirim oleh sistem.
Semua notifikasi sistem (karyawan, HR Admin, pimpinan) dicatat di sini.

---

| Field           | Type      | Required | Description                                  |
| --------------- | --------- | :------: | -------------------------------------------- |
| notification_id | Integer   | Yes      | ID unik notifikasi (primary key)             |
| employee_id     | Integer   | No       | FK ke Employee (NULL jika tujuan ke pimpinan)|
| phone_number    | String    | Yes      | Nomor WhatsApp tujuan pengiriman             |
| message_type    | Selection | Yes      | Jenis pesan (lihat nilai di bawah)           |
| message_content | Text      | Yes      | Isi pesan yang dikirimkan                    |
| message_status  | Selection | Yes      | Status pengiriman (lihat nilai di bawah)     |
| sent_at         | Datetime  | No       | Waktu pesan berhasil terkirim                |

---

## Nilai message_type

```text
attendance    → Notifikasi absensi berhasil
leave         → Notifikasi pengajuan izin/cuti/sakit
payroll       → Notifikasi slip gaji tersedia
report        → Laporan harian/bulanan ke pimpinan
notification  → Notifikasi umum lainnya
```

## Nilai message_status

```text
pending → Pesan antri, belum dikirim
sent    → Pesan berhasil terkirim
failed  → Pesan gagal terkirim (retry akan dilakukan)
```

---

# USER ACCOUNT

## Entity

System User

## Description

Menyimpan akun login untuk karyawan dan HR Admin.
Pimpinan tidak memiliki akun sistem.

---

| Field         | Type      | Required | Description                                  |
| ------------- | --------- | :------: | -------------------------------------------- |
| user_id       | Integer   | Yes      | ID unik user (primary key)                   |
| employee_id   | Integer   | Yes      | FK ke tabel Employee                         |
| username      | String    | Yes      | Username untuk login (unik)                  |
| password_hash | String    | Yes      | Password yang sudah di-hash (bcrypt)         |
| role          | Selection | Yes      | Hak akses (lihat nilai di bawah)             |
| last_login    | Datetime  | No       | Waktu terakhir login berhasil                |
| is_active     | Boolean   | Yes      | Status aktif akun                            |

---

## Nilai role

```text
employee    → Karyawan biasa (akses terbatas ke data sendiri)
hr_admin    → HR Admin (akses penuh ke semua data HRIS)
```

---

# REPORTING

## Entity

Generated Report

## Description

Menyimpan history laporan yang pernah di-generate oleh HR Admin.

---

| Field        | Type      | Required | Description                                   |
| ------------ | --------- | :------: | --------------------------------------------- |
| report_id    | Integer   | Yes      | ID unik report (primary key)                  |
| report_type  | Selection | Yes      | Jenis report (lihat nilai di bawah)           |
| generated_by | Integer   | Yes      | FK ke employee_id HR Admin yang generate      |
| generated_at | Datetime  | Yes      | Waktu report di-generate                      |
| file_url     | String    | Yes      | Path atau URL file hasil report               |

---

## Nilai report_type

```text
attendance_daily    → Rekap absensi harian
attendance_monthly  → Rekap absensi bulanan
leave_report        → Rekap pengajuan izin/cuti/sakit
payroll_report      → Rekap payroll bulanan
overtime_report     → Rekap lembur karyawan
```

---

# BUSINESS RULES RINGKASAN

## Attendance

* Sumber utama absensi adalah mesin fingerprint.
* Jika tidak ada absensi, izin, cuti, atau sakit pada hari kerja → status otomatis Alpha.
* Jam kerja minimum adalah 8 jam per hari.
* Jam kerja di atas 8 jam dihitung sebagai lembur (overtime).

---

## Leave

* Semua pengajuan (izin, cuti, sakit) memerlukan approval HR Admin.
* Status awal semua pengajuan adalah `pending`.
* Sakit wajib melampirkan surat dokter — disimpan di entity Medical Certificate.
* Izin boleh melampirkan dokumen pendukung — bersifat opsional.
* Cuti tidak memerlukan lampiran apapun.
* Izin dan cuti sama-sama mengurangi kuota cuti karyawan tetap.
* Freelance hanya bisa mengajukan izin dan sakit — tidak bisa mengajukan cuti.

---

## Payroll

* Payroll dihitung bulanan, dibayarkan tanggal 28.
* Komponen: gaji pokok + lembur + tunjangan - alpha_deduction - pph21.
* alpha_deduction dihitung prorata dari gaji pokok berdasarkan jumlah hari alpha.
* pph21_amount dihitung berdasarkan tarif progresif sesuai UU PPh Pasal 17.
* Notifikasi slip gaji dikirim via WhatsApp — tidak ada email.

---

## WhatsApp

* Digunakan untuk semua notifikasi karyawan dan HR Admin.
* Digunakan untuk semua laporan ke pimpinan.
* Tidak ada notifikasi via email di sistem ini.

---

## Employee Type

### Tetap

Hak yang dimiliki:

* Attendance (absensi fingerprint)
* Izin (dengan atau tanpa lampiran)
* Cuti (potongan kuota cuti)
* Sakit (wajib lampirkan surat dokter)
* Payroll bulanan
* Slip gaji

### Freelance

Hak yang dimiliki:

* Attendance (absensi fingerprint)
* Izin (dengan atau tanpa lampiran)
* Sakit (wajib lampirkan surat dokter)
* Payroll bulanan
* Slip gaji

Tidak mendapatkan:

* Cuti (tidak ada hak dan tidak ada kuota cuti)