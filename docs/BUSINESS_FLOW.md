# BUSINESS_FLOW.md

# HRIS ODOO 19 - BUSINESS FLOW & ROLE MATRIX

Version: 1.1
Status: Revised — Kontradiksi telah diselesaikan
Tanggal Revisi: Juni 2026

---

# CATATAN REVISI

Perubahan dari versi 1.0:

1. Ditambahkan klarifikasi bahwa HR Admin tetap bisa melakukan absensi via fingerprint sebagai karyawan.
2. Diperbarui aturan lampiran pengajuan: hanya sakit yang wajib lampiran, izin dan cuti opsional.
3. Dihapus referensi email notifikasi — seluruh notifikasi hanya via WhatsApp.
4. Ditambahkan aturan validasi tipe karyawan pada pengajuan cuti (Freelance tidak bisa mengajukan cuti).
5. Diseragamkan istilah status pengajuan menjadi `pending` di seluruh dokumen.

---

# DESKRIPSI SISTEM

HRIS (Human Resource Information System) dibangun di atas platform Odoo 19 Community.
Sistem ini mengelola seluruh proses HR mulai dari data karyawan, absensi, pengajuan izin dan cuti,
hingga penggajian dan pelaporan.

---

# ROLE YANG DIGUNAKAN

Sistem menggunakan tiga role:

1. **Karyawan** — Pengguna utama yang mengakses data miliknya sendiri.
2. **HR Admin** — Administrator HR dengan akses penuh ke seluruh data HRIS.
3. **Pimpinan** — Tidak memiliki akun sistem. Hanya menerima laporan via WhatsApp.

> Catatan: HR Admin juga adalah karyawan perusahaan. Untuk keperluan absensi,
> HR Admin menggunakan mesin fingerprint seperti karyawan biasa. Sistem mencatat
> absensi HR Admin secara otomatis dari fingerprint, tanpa akses khusus di UI absensi.

---

# MATRIKS HAK AKSES

## Akses Sistem Umum

| Fitur                | Karyawan | HR Admin | Pimpinan |
| -------------------- | :------: | :------: | :------: |
| Login Sistem         | ✅        | ✅        | ❌        |
| Logout Sistem        | ✅        | ✅        | ❌        |
| Ubah Password        | ✅        | ✅        | ❌        |
| Lihat Dashboard      | ✅        | ✅        | ❌        |
| Lihat Profil Sendiri | ✅        | ✅        | ❌        |
| Edit Profil Sendiri  | ✅        | ✅        | ❌        |

---

## Employee Management

| Fitur                       | Karyawan | HR Admin | Pimpinan |
| --------------------------- | :------: | :------: | :------: |
| Lihat Data Karyawan Sendiri | ✅        | ✅        | ❌        |
| Lihat Semua Karyawan        | ❌        | ✅        | ❌        |
| Tambah Karyawan             | ❌        | ✅        | ❌        |
| Edit Karyawan               | ❌        | ✅        | ❌        |
| Hapus Karyawan              | ❌        | ✅        | ❌        |
| Kelola Departemen           | ❌        | ✅        | ❌        |
| Kelola Jabatan              | ❌        | ✅        | ❌        |
| Kelola Lokasi Kerja         | ❌        | ✅        | ❌        |
| Kelola Jadwal Kerja         | ❌        | ✅        | ❌        |

---

## Attendance Management

| Fitur                    | Karyawan | HR Admin | Pimpinan |
| ------------------------ | :------: | :------: | :------: |
| Absensi via Fingerprint  | ✅        | ✅ *      | ❌        |
| Lihat Absensi Sendiri    | ✅        | ✅        | ❌        |
| Lihat Semua Absensi      | ❌        | ✅        | ❌        |
| Koreksi Absensi Manual   | ❌        | ✅        | ❌        |
| Kelola Aturan Attendance | ❌        | ✅        | ❌        |
| Kelola Fingerprint       | ❌        | ✅        | ❌        |
| Sinkronisasi Fingerprint | ❌        | ✅        | ❌        |

> *) HR Admin melakukan absensi via mesin fingerprint seperti karyawan biasa.
>    HR Admin tidak memiliki tombol atau form absensi manual di dalam sistem.
>    Absensi HR Admin dicatat otomatis dari log fingerprint yang disinkronisasi ke sistem.

---

## Leave Management — Izin

| Fitur                          | Karyawan | HR Admin | Pimpinan |
| ------------------------------ | :------: | :------: | :------: |
| Ajukan Izin                    | ✅        | ❌        | ❌        |
| Upload Lampiran Izin (opsional)| ✅        | ❌        | ❌        |
| Lihat Izin Sendiri             | ✅        | ✅        | ❌        |
| Lihat Semua Izin               | ❌        | ✅        | ❌        |
| Approve Izin                   | ❌        | ✅        | ❌        |
| Reject Izin                    | ❌        | ✅        | ❌        |

> Catatan: Lampiran pada pengajuan izin bersifat **opsional**.
> Karyawan dapat melampirkan dokumen pendukung jika diperlukan, tetapi tidak diwajibkan.

---

## Leave Management — Cuti

| Fitur                    | Karyawan Tetap | Freelance | HR Admin | Pimpinan |
| ------------------------ | :------------: | :-------: | :------: | :------: |
| Ajukan Cuti              | ✅              | ❌         | ❌        | ❌        |
| Lihat Cuti Sendiri       | ✅              | ❌         | ✅        | ❌        |
| Lihat Semua Cuti         | ❌              | ❌         | ✅        | ❌        |
| Approve Cuti             | ❌              | ❌         | ✅        | ❌        |
| Reject Cuti              | ❌              | ❌         | ✅        | ❌        |
| Kelola Kuota Cuti        | ❌              | ❌         | ✅        | ❌        |

> Catatan: Karyawan **Freelance tidak memiliki hak cuti**.
> Sistem wajib memvalidasi `employee_type` sebelum menerima pengajuan cuti.
> Jika karyawan bertipe freelance mencoba mengajukan cuti, sistem mengembalikan error
> dengan pesan: "Tipe karyawan freelance tidak memiliki hak cuti."

---

## Medical Leave — Sakit

| Fitur                      | Karyawan | HR Admin | Pimpinan |
| -------------------------- | :------: | :------: | :------: |
| Ajukan Sakit               | ✅        | ❌        | ❌        |
| Upload Surat Dokter (wajib)| ✅        | ❌        | ❌        |
| Lihat Surat Dokter Sendiri | ✅        | ✅        | ❌        |
| Lihat Semua Surat Dokter   | ❌        | ✅        | ❌        |
| Approve Surat Dokter       | ❌        | ✅        | ❌        |
| Reject Surat Dokter        | ❌        | ✅        | ❌        |

> Catatan: Surat dokter atau bukti medis bersifat **wajib (required)** untuk pengajuan sakit.
> Tanpa lampiran, sistem tidak akan memproses pengajuan sakit.

---

## Payroll Management

| Fitur                   | Karyawan | HR Admin | Pimpinan |
| ----------------------- | :------: | :------: | :------: |
| Lihat Slip Gaji Sendiri | ✅        | ✅        | ❌        |
| Download Slip Gaji      | ✅        | ✅        | ❌        |
| Lihat Semua Slip Gaji   | ❌        | ✅        | ❌        |
| Generate Payroll        | ❌        | ✅        | ❌        |
| Kelola Payroll          | ❌        | ✅        | ❌        |
| Kelola PPh21            | ❌        | ✅        | ❌        |
| Kelola Potongan         | ❌        | ✅        | ❌        |
| Kelola Tunjangan        | ❌        | ✅        | ❌        |

---

## Reporting

| Fitur                  | Karyawan | HR Admin | Pimpinan |
| ---------------------- | :------: | :------: | :------: |
| Lihat Laporan Absensi  | ❌        | ✅        | ❌        |
| Lihat Laporan Izin     | ❌        | ✅        | ❌        |
| Lihat Laporan Cuti     | ❌        | ✅        | ❌        |
| Lihat Laporan Payroll  | ❌        | ✅        | ❌        |
| Generate Rekap Harian  | ❌        | ✅        | ❌        |
| Generate Rekap Bulanan | ❌        | ✅        | ❌        |

---

# NOTIFIKASI WHATSAPP

> **Penting:** Seluruh notifikasi sistem menggunakan **WhatsApp saja**.
> Tidak ada notifikasi via email. Email tidak digunakan dalam sistem ini.

---

## Notifikasi yang Diterima Karyawan

Karyawan menerima notifikasi WhatsApp untuk kejadian berikut:

* Absensi masuk berhasil tercatat dari fingerprint
* Pengajuan izin berhasil dikirim (status: pending)
* Izin disetujui oleh HR Admin
* Izin ditolak oleh HR Admin
* Cuti disetujui oleh HR Admin (hanya karyawan tetap)
* Cuti ditolak oleh HR Admin (hanya karyawan tetap)
* Sakit disetujui oleh HR Admin
* Sakit ditolak oleh HR Admin
* Slip gaji tersedia dan siap diunduh

---

## Notifikasi yang Diterima HR Admin

HR Admin menerima notifikasi WhatsApp untuk kejadian berikut:

* Ada pengajuan izin baru dari karyawan
* Ada pengajuan cuti baru dari karyawan tetap
* Ada pengajuan sakit baru dari karyawan
* Sinkronisasi fingerprint gagal
* Error saat proses generate payroll

---

## Notifikasi yang Diterima Pimpinan

Pimpinan menerima laporan WhatsApp secara otomatis:

* Rekap absensi harian (dikirim setiap akhir hari kerja)
* Rekap absensi bulanan (dikirim setiap awal bulan)
* Rekap keterlambatan karyawan
* Rekap ketidakhadiran karyawan (alpha)
* Ringkasan payroll bulanan (dikirim setelah payroll diproses)

---

# EMPLOYEE TYPE MATRIX

## Karyawan Tetap

Karyawan tetap mendapatkan akses penuh ke seluruh fitur HRIS:

* Attendance (absensi via fingerprint)
* Izin (pengajuan dan tracking)
* Cuti (pengajuan, tracking, dan kuota)
* Sakit (pengajuan dengan surat dokter)
* Payroll bulanan
* Slip gaji
* Notifikasi WhatsApp

---

## Freelance

Karyawan freelance mendapatkan akses terbatas:

* Attendance (absensi via fingerprint)
* Izin (pengajuan dan tracking)
* Sakit (pengajuan dengan surat dokter)
* Payroll bulanan
* Slip gaji
* Notifikasi WhatsApp

Karyawan freelance **tidak mendapatkan**:

* Cuti (tidak ada hak cuti, tidak ada kuota cuti)
* Sistem akan menolak pengajuan cuti dari karyawan bertipe freelance

---

# BUSINESS RULES

## Attendance

* Sumber utama absensi adalah mesin fingerprint.
* Tidak ada absensi manual dari luar sistem fingerprint.
* HR Admin melakukan absensi via fingerprint seperti karyawan biasa — bukan via UI sistem.
* Tidak ada pencatatan keterlambatan secara eksplisit (hanya tercatat di worked_hours).
* Tidak ada approval keterlambatan.
* Tidak ada pengajuan lembur oleh karyawan.
* Jika karyawan tidak memiliki catatan absensi, izin, cuti, atau sakit pada hari kerja,
  maka status kehadiran otomatis menjadi **Alpha**.

---

## Overtime (Lembur)

* Lembur dihitung **otomatis oleh sistem**, tidak memerlukan pengajuan.
* Jam kerja minimum per hari adalah **8 jam**.
* Jam kerja di bawah 8 jam dianggap normal, tidak ada potongan.
* Jam kerja di atas 8 jam dihitung sebagai lembur.
* Contoh: Masuk 08:00, pulang 18:00 → 10 jam kerja → 2 jam lembur.
* Nominal lembur dihitung berdasarkan formula yang didefinisikan di konfigurasi payroll.
* Hasil perhitungan lembur masuk ke komponen `overtime_amount` di payroll.

---

## Pengajuan Leave (Izin, Cuti, Sakit)

Aturan lampiran per jenis pengajuan:

| Jenis Pengajuan | Lampiran     | Keterangan                                      |
| --------------- | ------------ | ----------------------------------------------- |
| Izin            | Opsional     | Karyawan boleh melampirkan dokumen, tidak wajib |
| Cuti            | Tidak perlu  | Tidak memerlukan lampiran apapun                |
| Sakit           | **Wajib**    | Surat dokter atau bukti medis harus dilampirkan |

* Semua pengajuan memerlukan approval dari HR Admin.
* Izin mengurangi kuota cuti karyawan tetap.
* Freelance hanya bisa mengajukan izin dan sakit, tidak bisa cuti.
* Status awal semua pengajuan adalah `pending`.

---

## Approval

Seluruh proses approval dilakukan oleh **HR Admin**.

Proses yang memerlukan approval:

* Pengajuan izin
* Pengajuan cuti (khusus karyawan tetap)
* Pengajuan sakit
* Koreksi data absensi

Tidak ada multi-level approval. Satu kali approval dari HR Admin sudah final.

---

## Payroll

* Payroll dihitung **bulanan**.
* Tanggal penggajian adalah **tanggal 28** setiap bulan.
* Komponen yang mempengaruhi payroll:
  - Gaji pokok (dari kontrak karyawan)
  - Tunjangan
  - Lembur (dihitung otomatis dari attendance)
  - Potongan alpha (tidak hadir tanpa keterangan)
  - PPh21 (dihitung berdasarkan penghasilan kena pajak)
* Formula PPh21 dan tarif potongan alpha wajib dikonfigurasi di modul payroll sebelum
  proses generate dijalankan.
* Slip gaji dikirimkan ke karyawan via notifikasi WhatsApp bahwa slip tersedia.
* Tidak ada pengiriman slip via email.

---

## Pimpinan

* Pimpinan **tidak memiliki akun sistem**.
* Pimpinan **tidak memiliki akses dashboard**.
* Pimpinan hanya menerima laporan dan notifikasi melalui **WhatsApp**.
* Nomor WhatsApp pimpinan dikonfigurasi di pengaturan sistem oleh HR Admin.