# foundation/overrides/employee_master.py

import frappe
from hrms.overrides.employee_master import EmployeeMaster as HRMSEmployeeMaster


class EmployeeMaster(HRMSEmployeeMaster):
    """
    Custom Employee class that ignores naming_series
    and uses custom_canonical_id as the document name.
    """

    def autoname(self):
        # make sure the field is filled
        if not self.custom_canonical_id:
            frappe.throw("Custom Canonical ID is required for Employee naming.")

        # use the field as the primary key
        self.name = self.custom_canonical_id
