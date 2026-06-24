# -*- coding: utf-8 -*-
<<<<<<< HEAD

class PayrollService:
    """Placeholder service untuk payroll."""

    def list_payroll(self, filters, page=1, per_page=20):
        raise NotImplementedError

    def generate_payroll(self, month, year):
        raise NotImplementedError

=======
import logging
from datetime import datetime, time, timedelta

# pyrefly: ignore [missing-import]
from odoo import models, api, _
# pyrefly: ignore [missing-import]
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

# -------------------------------------------------------------------
# BPJS Configuration Constants
# (Move to ir.config_parameter or res.config.settings for production)
# -------------------------------------------------------------------
# BPJS Kesehatan — employee portion (1% of gross, capped at max salary base)
BPJS_KES_EMPLOYEE_RATE = 0.01
BPJS_KES_MAX_SALARY_BASE = 12_000_000  # IDR

# BPJS Ketenagakerjaan (JHT) — employee portion
BPJS_JHT_EMPLOYEE_RATE = 0.02

# BPJS Ketenagakerjaan (JP) — employee portion (capped)
BPJS_JP_EMPLOYEE_RATE = 0.01
BPJS_JP_MAX_SALARY_BASE = 10_042_300  # IDR (updated annually)

# Late penalty per occurrence
LATE_PENALTY_PER_OCCURRENCE = 50_000  # IDR

# TER Category mapping from x_tax_status
TAX_STATUS_TO_TER_CATEGORY = {
    'TK/0': 'A',
    'TK/1': 'A',
    'TK/2': 'B',
    'TK/3': 'B',
    'K/0': 'A',
    'K/1': 'B',
    'K/2': 'C',
    'K/3': 'C',
    'K/I/0': 'C',
    'K/I/1': 'C',
    'K/I/2': 'C',
    'K/I/3': 'C',
}


class PayrollService(models.AbstractModel):
    """
    Service layer for payroll computation.
    Fat service — contains all business logic for:
      - Gross salary calculation
      - Late penalty deduction
      - BPJS deduction computation
      - PPh 21 TER calculation (Indonesian tax)
      - Net salary (THP) computation
      - Payslip record creation/update
    """
    _name = 'hris.payroll.service'
    _description = 'Payroll Computation Service'

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @api.model
    def calculate_monthly_payroll(self, employee_id, month, year):
        """
        Calculate and persist the monthly payroll for a given employee.

        Args:
            employee_id (int): ID of the hr.employee record.
            month (int): Payroll month (1-12).
            year (int): Payroll year (e.g. 2026).

        Returns:
            dict: Payroll computation summary.
        """
        # --- Validate inputs ---
        employee = self.env['hr.employee'].sudo().browse(employee_id)
        if not employee.exists():
            raise UserError(_('Employee with ID %d not found.') % employee_id)
        if month < 1 or month > 12:
            raise UserError(_('Month must be between 1 and 12.'))
        if year < 2000:
            raise UserError(_('Year must be 2000 or later.'))

        _logger.info(
            'Calculating payroll for %s — period: %02d/%d',
            employee.name, month, year,
        )

        # --- 1. Gross salary ---
        gross_salary = self._calculate_gross_salary(employee)

        # --- 2. Late deduction ---
        late_count = self._count_late_days(employee, month, year)
        late_deduction = late_count * LATE_PENALTY_PER_OCCURRENCE

        # --- 3. BPJS deductions ---
        bpjs_deduction = self._calculate_bpjs(gross_salary)

        # --- 4. PPh 21 TER ---
        pph21_amount = self._calculate_pph21_ter(employee, gross_salary, month)

        # --- 5. Net salary (THP) ---
        net_salary = gross_salary - late_deduction - bpjs_deduction - pph21_amount

        # --- 6. Persist to payslip ---
        payslip = self._upsert_payslip(
            employee=employee,
            month=month,
            year=year,
            gross_salary=gross_salary,
            late_deduction=late_deduction,
            bpjs_deduction=bpjs_deduction,
            pph21_amount=pph21_amount,
            net_salary=net_salary,
        )

        result = {
            'payslip_id': payslip.id,
            'employee_name': employee.name,
            'period': f'{month:02d}/{year}',
            'gross_salary': gross_salary,
            'late_count': late_count,
            'late_deduction': late_deduction,
            'bpjs_deduction': bpjs_deduction,
            'pph21_amount': pph21_amount,
            'net_salary': net_salary,
        }

        _logger.info(
            'Payroll computed for %s: gross=%.0f, late_ded=%.0f, '
            'bpjs=%.0f, pph21=%.0f, net=%.0f',
            employee.name, gross_salary, late_deduction,
            bpjs_deduction, pph21_amount, net_salary,
        )
        return result

    # ------------------------------------------------------------------
    # Private computation methods
    # ------------------------------------------------------------------

    def _calculate_gross_salary(self, employee):
        """
        Calculate gross salary from the employee's contract.
        Gross = Base Wage + Allowances defined in the contract's struct.
        """
        contract = self.env['hr.contract'].sudo().search([
            ('employee_id', '=', employee.id),
            ('state', '=', 'open'),  # active/running contract
        ], limit=1)

        if not contract:
            raise UserError(
                _('No active contract found for employee "%s". '
                  'A running contract is required for payroll calculation.')
                % employee.name
            )

        base_wage = contract.wage or 0.0

        # Sum any additional allowances stored on the contract
        # (Odoo 19 hr_payroll may use struct-based rules; here we provide
        # a simplified approach that can be extended)
        allowances = 0.0
        if hasattr(contract, 'x_transport_allowance'):
            allowances += contract.x_transport_allowance or 0.0
        if hasattr(contract, 'x_meal_allowance'):
            allowances += contract.x_meal_allowance or 0.0
        if hasattr(contract, 'x_position_allowance'):
            allowances += contract.x_position_allowance or 0.0

        gross = base_wage + allowances
        _logger.debug(
            'Gross for %s: base=%s + allowances=%s = %s',
            employee.name, base_wage, allowances, gross,
        )
        return gross

    def _count_late_days(self, employee, month, year):
        """Count attendance records marked as late for the given period."""
        period_start = datetime(year, month, 1)
        if month == 12:
            period_end = datetime(year + 1, 1, 1)
        else:
            period_end = datetime(year, month + 1, 1)

        late_count = self.env['hr.attendance'].sudo().search_count([
            ('employee_id', '=', employee.id),
            ('check_in', '>=', period_start),
            ('check_in', '<', period_end),
            ('x_is_late', '=', True),
        ])
        _logger.debug(
            'Late count for %s in %02d/%d: %d',
            employee.name, month, year, late_count,
        )
        return late_count

    def _calculate_bpjs(self, gross_salary):
        """
        Calculate total BPJS employee contributions.
        Components:
          - BPJS Kesehatan: 1% of gross (capped at max salary base)
          - BPJS JHT: 2% of gross
          - BPJS JP: 1% of gross (capped at max salary base)
        """
        # BPJS Kesehatan
        kes_base = min(gross_salary, BPJS_KES_MAX_SALARY_BASE)
        bpjs_kes = kes_base * BPJS_KES_EMPLOYEE_RATE

        # BPJS JHT
        bpjs_jht = gross_salary * BPJS_JHT_EMPLOYEE_RATE

        # BPJS JP
        jp_base = min(gross_salary, BPJS_JP_MAX_SALARY_BASE)
        bpjs_jp = jp_base * BPJS_JP_EMPLOYEE_RATE

        total = bpjs_kes + bpjs_jht + bpjs_jp
        _logger.debug(
            'BPJS: kes=%.0f, jht=%.0f, jp=%.0f, total=%.0f',
            bpjs_kes, bpjs_jht, bpjs_jp, total,
        )
        return total

    def _calculate_pph21_ter(self, employee, gross_salary, month):
        """
        Calculate PPh 21 using the Indonesian TER method.

        For periods January to November (months 1-11):
          1. Map x_tax_status -> TER Category (A, B, or C).
          2. Query the hris.pph21.ter.table for the matching bracket.
          3. PPh 21 = gross_salary * rate.

        For December (month 12):
          December uses a yearly recalculation (not implemented here —
          returns 0 and logs a warning for future extension).
        """
        if month == 12:
            _logger.warning(
                'PPh 21 December recalculation not yet implemented for %s. '
                'Returning 0. Extend _calculate_pph21_ter_december().',
                employee.name,
            )
            return 0.0

        tax_status = employee.x_tax_status or 'TK/0'
        ter_category = TAX_STATUS_TO_TER_CATEGORY.get(tax_status, 'A')

        rate = self._lookup_ter_rate(ter_category, gross_salary)
        pph21 = gross_salary * (rate / 100.0)

        _logger.debug(
            'PPh 21 TER for %s: status=%s, cat=%s, gross=%.0f, rate=%.2f%%, pph21=%.0f',
            employee.name, tax_status, ter_category, gross_salary, rate, pph21,
        )
        return pph21

    def _lookup_ter_rate(self, category, gross_salary):
        """
        Look up the TER percentage from hris.pph21.ter.table
        for the given category and gross salary bracket.
        """
        TerTable = self.env['hris.pph21.ter.table'].sudo()

        # Find bracket where gross_salary falls within [gross_start, gross_end]
        # gross_end = 0 means unlimited upper bound
        record = TerTable.search([
            ('category', '=', category),
            ('gross_start', '<=', gross_salary),
            '|',
            ('gross_end', '>=', gross_salary),
            ('gross_end', '=', 0),
        ], order='gross_start desc', limit=1)

        if not record:
            _logger.warning(
                'No TER rate found for category=%s, gross=%.0f. '
                'Defaulting to 0%%. Please populate hris.pph21.ter.table.',
                category, gross_salary,
            )
            return 0.0

        return record.percentage

    def _upsert_payslip(self, employee, month, year, gross_salary,
                        late_deduction, bpjs_deduction, pph21_amount, net_salary):
        """
        Create or update an hr.payslip record for the given period.
        Uses the period's first and last day as date_from / date_to.
        """
        Payslip = self.env['hr.payslip'].sudo()

        date_from = datetime(year, month, 1).date()
        if month == 12:
            date_to = datetime(year, 12, 31).date()
        else:
            date_to = (datetime(year, month + 1, 1) - timedelta(days=1)).date()

        # Search for existing payslip in this period
        existing = Payslip.search([
            ('employee_id', '=', employee.id),
            ('date_from', '=', date_from),
            ('date_to', '=', date_to),
        ], limit=1)

        payslip_vals = {
            'x_gross_salary': gross_salary,
            'x_late_deduction': late_deduction,
            'x_bpjs_deduction': bpjs_deduction,
            'x_pph21_amount': pph21_amount,
            'x_net_salary': net_salary,
        }

        if existing:
            existing.write(payslip_vals)
            _logger.info('Updated payslip %s for %s', existing.number or existing.id, employee.name)
            return existing

        # Get the active contract for struct reference
        contract = self.env['hr.contract'].sudo().search([
            ('employee_id', '=', employee.id),
            ('state', '=', 'open'),
        ], limit=1)

        create_vals = {
            'employee_id': employee.id,
            'date_from': date_from,
            'date_to': date_to,
            'contract_id': contract.id if contract else False,
            'name': f'Payslip - {employee.name} - {month:02d}/{year}',
            **payslip_vals,
        }

        # Set struct_id if contract provides one
        if contract and hasattr(contract, 'struct_id') and contract.struct_id:
            create_vals['struct_id'] = contract.struct_id.id

        payslip = Payslip.create(create_vals)
        _logger.info('Created payslip %s for %s', payslip.id, employee.name)
        return payslip
>>>>>>> b86b2d617809ec4af00d64846d68a94259ce2543
