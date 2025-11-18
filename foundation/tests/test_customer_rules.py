# foundation/tests/test_customer_rules.py
from frappe.tests.utils import FrappeTestCase
import frappe

# ---- config (adjust if your fieldnames differ) -----------------------

# foundation/tests/test_customer_rules.py
TIER_FIELD = "custom_tier"
WASTE_TABLE = "Waste Pattern"          # 👈 child DocType name
SERVICE_TABLE = "Service Window"       # 👈 child DocType name


frappe.utils.logger.set_log_level("DEBUG")

logger = frappe.logger("tier", allow_site=True)


# ---- helpers ---------------------------------------------------------

def _ensure_territory_leaf() -> str:
    """
    Make sure there's a proper leaf Territory to satisfy any 'leaf-only' validator.
    Creates: Iran (group) -> Test Region (group) -> Test Province (group) -> Test Leaf County (leaf)
    Returns the leaf territory name.
    """
    def _mk(name, parent, is_group: int):
        if not frappe.db.exists("Territory", name):
            doc = frappe.get_doc({
                "doctype": "Territory",
                "territory_name": name,
                "parent_territory": parent,
                "is_group": is_group,
            })
            doc.flags.ignore_permissions = True
            doc.db_insert()

    _mk("Iran", "All Territories", 1)
    _mk("Test Region", "Iran", 1)
    _mk("Test Province", "Test Region", 1)
    _mk("Test Leaf County", "Test Province", 0)
    return "Test Leaf County"

def _row(table, **fields):
    return {"doctype": table, **fields}

def _make_customer(**kw):
    """
    Minimal-but-valid Customer for these tests.
    You can add more fields here if your site enforces extra mandatories.
    """
    
    territory = kw.pop("territory", None) or _ensure_territory_leaf()
    tier_val  = kw.pop(TIER_FIELD, "Small")
    logger.info(f"test tier {tier_val}")

    doc = frappe.get_doc({
        "doctype": "Customer",
        "customer_name": kw.pop("customer_name", "Test Cust"),
        "customer_type": kw.pop("customer_type", "Company"),
        "territory": territory,
        "custom_tier": tier_val,
        # Supplementary fields used by the hook:
        "tax_id": kw.pop("tax_id", None),
        "custom_site_hse_contact": kw.pop("custom_site_hse_contact", None),
        "custom_site_hse_mobile": kw.pop("custom_site_hse_mobile", None),
        "custom_waste_pattern": kw.pop("custom_waste_pattern", []),
        "custom_service_windows": kw.pop("custom_service_windows", []),
        **kw,
    })
    doc.flags.ignore_mandatory = True
    doc.flags.ignore_links = True
    doc.flags.ignore_tier_mandatory = False
    return doc

# ---- tests -----------------------------------------------------------

class TestCustomerTierRules(FrappeTestCase):
    def setUp(self):
        frappe.flags.in_test = True
        frappe.flags.mute_emails = True
        _ensure_territory_leaf()  # ensure tree exists

    def test_small_allows_missing_supplementaries(self):
        c = _make_customer(**{TIER_FIELD: "Small"})
        with self.assertRaises(frappe.ValidationError):
            c.insert(ignore_permissions=True)
        self.assertTrue(c.name)

    def test_medium_requires_taxid_hse_and_wastepattern(self):
        # Expect failure when required fields for Medium+ are missing

        c = _make_customer(**{TIER_FIELD: "Mid-High"})
        assert c.get("custom_tier") == "Mid-High", f"custom_tier is {c.get('custom_tier')!r}"
        with self.assertRaises(frappe.ValidationError):
            c.insert(ignore_permissions=True)

        # Fill required fields for Medium and try again
        setattr(c, "tax_id", "1234567890")
        setattr(c, "custom_site_hse_contact", "Contact X")
        setattr(c, "custom_site_hse_mobile", "09120000000")
        c.append(
            "custom_waste_pattern",
            _row(
                WASTE_TABLE,
                material_type="General",
                frequency_count=1,
                frequency_unit="Per Week",
            ),
        )

        c.insert(ignore_permissions=True)
        self.assertTrue(c.name)

    # def test_large_requires_service_windows_too(self):
    #     # With Medium+ requirements satisfied but no service window, Large should fail
    #     c = _make_customer(
    #         **{
    #             TIER_FIELD: "Large",
    #             "tax_id": "123",
    #             "site_hse_contact": "HSE Y",
    #             "site_hse_mobile": "09123334444",
    #             "waste_pattern": [
    #                 _row(WASTE_TABLE, material_type="General", frequency_count=2, frequency_unit="Per Week")
    #             ],
    #         }
    #     )
    #     with self.assertRaises(frappe.ValidationError):
    #         c.insert(ignore_permissions=True)

    #     # Add at least one service window → should pass
    #     c.service_windows = [_row(SERVICE_TABLE, weekday="Mon", shift="AM")]
    #     c.insert(ignore_permissions=True)
    #     self.assertTrue(c.name)
