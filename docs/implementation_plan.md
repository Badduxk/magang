# Audit Teknis Modul Employee — `hris_employee`

**Phase:** 02 — Employee (sesuai Task Roadmap)
**Tanggal Audit:** 2026-06-24
**Versi Dokumen Referensi:** 1.1

---

# Sumber Referensi yang Digunakan

| Dokumen               | Bagian yang Dirujuk                                                                                             |
| --------------------- | --------------------------------------------------------------------------------------------------------------- |
| AI_PROJECT_CONTEXT.md | Business Rules (L173–L184), Coding Rules (L607–L641), Security Rules (L645–L661), Module Dependency (L119–L169) |
| MODULE_MAPPING.md     | Section A. EMPLOYEES (L85–L177)                                                                                 |
| BUSINESS_FLOW.md      | Role Matrix — Employee Management (L60–L73), Employee Type Matrix (L219–L250)                                   |
| DATA_DICTIONARY.md    | Entity Employee (L126–L177), Entity Department (L180–L200), Entity Work Location (L203–L234)                    |
| API_CONTRACT.md       | Section Employee (L199–L401)                                                                                    |

---

# 1. Modul Odoo yang Akan Di-extend

Sesuai `MODULE_MAPPING.md — Section A`, modul Employee tidak perlu dibuat dari nol.

Yang dilakukan adalah **extend modul bawaan Odoo**.

| Modul Odoo        | Technical Name | Aksi                          |
| ----------------- | -------------- | ----------------------------- |
| Employees         | `hr`           | Extend — modul utama karyawan |
| Department        | `hr`           | Extend — sudah mencukupi      |
| Resource Calendar | `resource`     | Extend — jadwal kerja         |
| Work Location     | `hr`           | Extend — lokasi kerja         |

> **Kesimpulan MODULE_MAPPING (L169–L176):**
> Tidak perlu membuat modul karyawan baru. Cukup extend modul yang sudah ada.

## Modul Custom yang Dibuat

| Nama Modul    | Technical Name  |
| ------------- | --------------- |
| HRIS Employee | `hris_employee` |

Modul `hris_employee` adalah modul extend yang menambahkan field dan validasi bisnis HRIS ke model Odoo yang sudah ada.

---

# 2. Model yang Perlu Di-inherit

## 2.1 `hr.employee`

Sumber:

* MODULE_MAPPING.md L111–L130
* DATA_DICTIONARY.md L126–L177

```python
_inherit = 'hr.employee'
```

Digunakan untuk menambahkan field HRIS yang tidak tersedia pada Odoo bawaan.

---

## 2.2 `hr.employee.public`

```python
_inherit = 'hr.employee.public'
```

Pada Odoo 19, model ini digunakan untuk user non-HR.

Field custom yang perlu terlihat oleh user portal harus ikut ditambahkan pada model ini.

---

## 2.3 `hr.department`

```python
_inherit = 'hr.department'
```

Field bawaan Odoo sudah cukup.

Tambahan yang diperlukan:

* `department_code`

---

## 2.4 `hr.work.location`

```python
_inherit = 'hr.work.location'
```

Perlu ditambahkan field tambahan sesuai DATA_DICTIONARY.

---

## 2.5 `resource.calendar`

Tidak perlu extend pada phase ini.

Model ini akan lebih relevan di:

```text
Phase 03 → hris_attendance
```

Cukup menggunakan field bawaan:

```python
resource_calendar_id
```

---

# 3. Field Baru yang Diperlukan

## 3.1 Field Baru pada `hr.employee`

### Gap Analysis

| Field HRIS          | Field Odoo                | Status | Aksi             |
| ------------------- | ------------------------- | ------ | ---------------- |
| employee_id         | id                        | ✅      | Gunakan bawaan   |
| employee_code       | -                         | ❌      | Tambah field     |
| nik                 | identification_id         | ⚠️     | Mapping          |
| full_name           | name                      | ✅      | Gunakan bawaan   |
| email               | work_email                | ✅      | Gunakan bawaan   |
| phone_number        | mobile_phone              | ✅      | Gunakan bawaan   |
| photo               | image_1920                | ✅      | Gunakan bawaan   |
| employee_type       | employee_type             | ⚠️     | Override/Mapping |
| department_id       | department_id             | ✅      | Gunakan bawaan   |
| job_position        | job_id/job_title          | ✅      | Gunakan bawaan   |
| manager_id          | parent_id                 | ✅      | Gunakan bawaan   |
| npwp_number         | -                         | ❌      | Tambah field     |
| bank_name           | bank_account_id           | ⚠️     | Evaluasi         |
| bank_account_number | bank_account_id           | ⚠️     | Evaluasi         |
| join_date           | -                         | ❌      | Tambah field     |
| status              | active + departure_reason | ⚠️     | Tambah field     |

---

## Field Wajib Ditambahkan

| No | Field           | Type      | Required | Constraint               |
| -- | --------------- | --------- | -------- | ------------------------ |
| 1  | employee_code   | Char      | Yes      | Unique                   |
| 2  | nik             | Char(16)  | Yes      | Unique                   |
| 3  | npwp_number     | Char      | Yes      | -                        |
| 4  | join_date       | Date      | Yes      | -                        |
| 5  | employee_status | Selection | Yes      | active/inactive/resigned |

---

## Keputusan Desain

### Keputusan 1 — Employee Type

Odoo:

```text
employee
student
freelance
```

HRIS:

```text
tetap
freelance
```

Pilihan:

### A. Override Selection

Pro:

* Bersih

Kontra:

* Risiko konflik internal Odoo

### B. Field Baru

Misal:

```python
hris_employee_type
```

Pro:

* Aman

Kontra:

* Duplikasi field

### C. Mapping

```text
employee → tetap
freelance → freelance
```

**Rekomendasi:** A (dengan testing menyeluruh).

---

### Keputusan 2 — NIK

Gunakan:

```python
identification_id
```

Tambahkan validasi:

* 16 digit
* Unique

Tidak perlu field baru.

---

### Keputusan 3 — Bank

Gunakan model bawaan:

```python
res.partner.bank
```

Jangan membuat field baru.

Controller API akan melakukan flattening response.

---

## 3.2 Field Baru pada `hr.department`

| Field           | Type | Required |
| --------------- | ---- | -------- |
| department_code | Char | Yes      |

Constraint:

```text
Unique
Format: DEPT-XX
```

---

## 3.3 Field Baru pada `hr.work.location`

| Field           | Type      | Required |
| --------------- | --------- | -------- |
| address         | Text      | Yes      |
| city            | Char      | Yes      |
| province        | Char      | Yes      |
| postal_code     | Char      | No       |
| location_status | Selection | Yes      |

Pilihan status:

```text
active
inactive
```

---

# 4. Security Group

## 4.1 Security Groups

| XML ID              | Nama          | Implied             |
| ------------------- | ------------- | ------------------- |
| group_hris_employee | HRIS Employee | base.group_user     |
| group_hris_hr_admin | HRIS HR Admin | group_hris_employee |

> Security group dibuat di modul `hris_base`.

---

## 4.2 Access Rights

| Model            | Group    | R | W | C | D |
| ---------------- | -------- | - | - | - | - |
| hr.employee      | Employee | ✅ | ❌ | ❌ | ❌ |
| hr.employee      | HR Admin | ✅ | ✅ | ✅ | ✅ |
| hr.department    | Employee | ✅ | ❌ | ❌ | ❌ |
| hr.department    | HR Admin | ✅ | ✅ | ✅ | ✅ |
| hr.work.location | Employee | ✅ | ❌ | ❌ | ❌ |
| hr.work.location | HR Admin | ✅ | ✅ | ✅ | ✅ |

---

## 4.3 Record Rules

### Employee Own Data

```python
[('id', '=', user.employee_id.id)]
```

### HR Admin

```python
[(1, '=', 1)]
```

---

# 5. View yang Dimodifikasi

Semua menggunakan:

```xml
inherit_id
```

---

## 5.1 Employee Form

Extend:

```xml
hr.view_employee_form
```

Tambahkan:

| Field           | Lokasi              |
| --------------- | ------------------- |
| employee_code   | Header              |
| nik             | Private Information |
| npwp_number     | Private Information |
| join_date       | Work Information    |
| employee_status | Header              |

---

## 5.2 Employee Tree

Extend:

```xml
hr.view_employee_tree
```

Tambahan kolom:

```text
employee_code
employee_type
employee_status
join_date
```

---

## 5.3 Employee Search

Tambahan filter:

```text
Employee Type
Employee Status
Department
```

Searchable:

```text
employee_code
nik
```

---

## 5.4 Department Form

Tambahkan:

```text
department_code
```

---

## 5.5 Work Location Form

Tambahkan:

```text
location_status
```

---

# 6. API yang Diperlukan

## Endpoint Employee

| Method | Endpoint               | Role     |
| ------ | ---------------------- | -------- |
| GET    | /api/v1/employees/me   | Employee |
| PUT    | /api/v1/employees/me   | Employee |
| GET    | /api/v1/employees      | HR Admin |
| GET    | /api/v1/employees/{id} | HR Admin |
| POST   | /api/v1/employees      | HR Admin |
| PUT    | /api/v1/employees/{id} | HR Admin |
| DELETE | /api/v1/employees/{id} | HR Admin |

---

## Format Response

### Success

```json
{
  "success": true,
  "message": "Success",
  "data": {}
}
```

### Error

```json
{
  "success": false,
  "message": "Validation Error",
  "errors": [
    {
      "field": "nik",
      "message": "Must be 16 digits"
    }
  ]
}
```

---

## Soft Delete

```python
active = False
employee_status = 'resigned'
```

---

# 7. Risiko Implementasi

## Risiko Tinggi

| Risiko                 | Dampak                    | Mitigasi                 |
| ---------------------- | ------------------------- | ------------------------ |
| Override employee_type | Konflik internal Odoo     | Regression testing       |
| Security group overlap | Hak akses tidak konsisten | Mapping group yang jelas |

---

## Risiko Sedang

| Risiko                 | Mitigasi                |
| ---------------------- | ----------------------- |
| Constraint NIK         | Gunakan @api.constrains |
| Sequence employee_code | Gunakan ir.sequence     |
| Bank relation          | Flatten di API          |

---

## Risiko Rendah

| Risiko           | Mitigasi              |
| ---------------- | --------------------- |
| join_date        | Pure add field        |
| View inheritance | Gunakan XML ID stabil |

---

# 8. Dependency

## Direct Dependency

```yaml
hris_employee:
  depends:
    - hr
    - hris_base
```

---

## Dependency Tree

```text
hris_employee
├── hr
│   ├── base
│   ├── resource
│   └── mail
└── hris_base
```

---

## Modul Downstream

| Modul           | Alasan           |
| --------------- | ---------------- |
| hris_attendance | Data employee    |
| hris_timeoff    | Employee type    |
| hris_payroll    | NPWP             |
| hris_portal     | Employee profile |
| hris_reporting  | Reporting        |

---

## Urutan Implementasi

```text
Phase 01 → hris_base
Phase 02 → hris_employee
```

`hris_base` harus selesai terlebih dahulu.

---

# Open Questions

## Q1

Apakah `hris_base` sudah selesai diimplementasikan?

---

## Q2

Untuk `employee_type`, pilih:

```text
A. Override bawaan Odoo
B. Field custom baru
```

---

## Q3

Untuk NIK:

```text
A. Gunakan identification_id
B. Buat field baru nik
```

---

## Q4

Untuk rekening bank:

```text
A. Gunakan res.partner.bank
B. Field Char langsung di employee
```

---

# Struktur Modul

```text
hris_employee/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── hr_employee.py
│   ├── hr_department.py
│   └── hr_work_location.py
├── security/
│   ├── ir.model.access.csv
│   └── hris_employee_security.xml
├── views/
│   ├── hr_employee_views.xml
│   ├── hr_department_views.xml
│   └── hr_work_location_views.xml
├── data/
│   └── ir_sequence_data.xml
└── README.md
```

**Estimasi Total File:** 12

---

# Verification Plan

## Automated Test

```bash
python -m pytest

odoo-bin -d test_db -i hris_employee --test-enable
```

---

## Manual Verification Checklist

* [ ] Install module berhasil
* [ ] Upgrade module berhasil
* [ ] Field baru muncul di Employee Form
* [ ] Employee hanya melihat data sendiri
* [ ] HR Admin dapat CRUD seluruh employee
* [ ] employee_code auto-generate
* [ ] Validasi NIK 16 digit berjalan
* [ ] Soft delete berjalan sesuai spesifikasi

```
```
