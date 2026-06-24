# -*- coding: utf-8 -*-
# pyrefly: ignore [missing-import]
from odoo import models, fields


class HrAttendance(models.Model):
    """
    Extension of hr.attendance to track lateness.
    Thin model — only fields, no business logic.
    """
    _inherit = 'hr.attendance'

    x_is_late = fields.Boolean(
        string='Is Late',
        default=False,
        help='Automatically set to True if the employee checked in after 08:00 AM.',
    )
