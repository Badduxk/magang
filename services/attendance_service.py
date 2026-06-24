# -*- coding: utf-8 -*-

class AttendanceService:
    """Placeholder service untuk attendance.

    Fungsi-fungsi inti (generate summary/records, correction processing) akan diimplementasikan di tahap berikutnya.
    """

    def get_my_attendance(self, employee_id, month=None, page=1, per_page=20):
        raise NotImplementedError

    def list_attendance(self, filters, page=1, per_page=20):
        raise NotImplementedError

    def correct_attendance(self, employee_id, attendance_date, check_in, check_out, reason):
        raise NotImplementedError

