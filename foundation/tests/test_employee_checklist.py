# foundation/tests/test_employee_checklist.py
from frappe.tests.utils import FrappeTestCase
from unittest.mock import patch
import frappe

# ---- helpers ----------------------------------------------------------

def _ensure_designation(name: str = "Truck Driver 6T") -> str:
    """Make sure a Designation exists so org-role hook won't fail."""
    if not frappe.db.exists("Designation", name):
        doc = frappe.get_doc({"doctype": "Designation", "designation_name": name})
        doc.flags.ignore_permissions = True
        doc.db_insert()
    return name

def _attach(emp_name, fname, bytes_=b"dummy"):
    # Patch EXACT symbols used inside File doctype for safe in-memory content
    with patch("frappe.core.doctype.file.file.strip_exif_data",
               side_effect=lambda content, ct=None: content), \
         patch("frappe.core.doctype.file.file.pdf_contains_js",
               return_value=False):

        return frappe.get_doc({
            "doctype": "File",
            "file_name": fname,                    # e.g. "meli-front.jpg"
            "content": bytes_,                     # arbitrary bytes
            "content_type": "application/octet-stream",
            "is_private": 1,
            "attached_to_doctype": "Employee",
            "attached_to_name": emp_name,
        }).insert(ignore_permissions=True).name

# ---- tests ------------------------------------------------------------

class TestEmployeeChecklist(FrappeTestCase):
    def setUp(self):
        frappe.flags.in_test = True
        frappe.flags.mute_emails = True
        _ensure_designation()

    def test_checklist_updates_on_file_events(self):
        # Create a minimal-but-valid Employee so your hooks pass:
        # - identity hook needs custom_national_code
        # - org-role hook needs org_track + designation
        emp = frappe.get_doc({
            "doctype": "Employee",
            "employee_name": "Test Emp",
            "custom_national_code": "1234567890",
            "org_track": "Administrative",
            "designation": "Truck Driver 6T",
        })

        # We’re NOT testing the ID-scan policy here, so skip it:
        # Your id_scan hook should have: if doc.flags._skip_id_scan: return
        emp.flags._skip_id_scan = True

        # Keep DB mandatories out of the way for fields irrelevant to this test
        emp.flags.ignore_mandatory = True
        emp.insert(ignore_permissions=True)

        # Your after_insert Employee hook should create a Checklist row
        chk_name = frappe.db.get_value("Employee Checklist",
                                       {"custom_employee": emp.name},
                                       "name")
        self.assertIsNotNone(chk_name)
        chk = frappe.get_doc("Employee Checklist", chk_name)

        # Attach files to the Employee
        _attach(emp.name, "meli-front.jpg")       # front of national card
        _attach(emp.name, "meli-back.jpg")        # back of national card
        _attach(emp.name, "shen-full.pdf")        # full shenasnameh
        _attach(emp.name, "degree-latest.pdf")    # last degree
        _attach(emp.name, "contract-signed.pdf")  # signed contract

        chk.reload()
        self.assertEqual(int(chk.custom_id_card_both_sides or 0), 1)
        self.assertEqual(int(chk.custom_shenasnameh_full or 0), 1)
        self.assertEqual(int(chk.custom_education_last_degree or 0), 1)
        self.assertEqual(int(chk.custom_signed_contract or 0), 1)

        # Delete one file and verify checklist updates
        file_to_delete = frappe.db.get_value(
            "File",
            {
                "attached_to_doctype": "Employee",
                "attached_to_name": emp.name,
                "file_name": ["like", "%shen%"],  # matches shen-full.pdf
            },
            "name",
        )
        frappe.delete_doc("File", file_to_delete, force=True)

        chk.reload()
        self.assertEqual(int(chk.custom_shenasnameh_full or 0), 0)
