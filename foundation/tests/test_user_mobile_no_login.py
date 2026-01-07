import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.auth import LoginManager
from frappe.exceptions import AuthenticationError


class TestUserMobileUsername(FrappeTestCase):
    def _make_user(self, mobile_no: str, password: str = "TestPassword123"):
        """Helper to create a test System User with a given mobile_no."""
        email = f"mobile.test.{frappe.generate_hash(length=6)}@example.com"

        user = frappe.get_doc({
            "doctype": "User",
            "email": email,
            "first_name": "Mobile Test",
            "user_type": "System User",
            "mobile_no": mobile_no,
            "send_welcome_email": 0,
            "new_password": password,
        })

        user.insert(ignore_permissions=True)
        return user

    # --- existing tests for username/mobile_no here ---
    # test_username_set_on_insert, test_username_updates_when_mobile_changes, etc.

    def _login(self, usr: str, pwd: str) -> str:
        """
        Perform a login like the real login API:
        - usr: what user types in the login form (email or mobile)
        - pwd: password

        Returns frappe.session.user on success.
        """
        # Clear any previous login info
        frappe.local.login_manager = None
        frappe.local.form_dict = frappe._dict(usr=usr, pwd=pwd)

        LoginManager()  # authenticate + post_login

        return frappe.session.user

    def test_can_login_with_mobile_number(self):
        """User should be able to log in using mobile_no as usr."""
        mobile = "09123334444"
        password = "TestPassword123"

        user = self._make_user(mobile_no=mobile, password=password)

        # Reload to ensure hooks (validate) have run
        user = frappe.get_doc("User", user.name)

        # Sanity check: our hook ran
        self.assertEqual(user.username, mobile)

        # Try login with mobile number (what user types in login form)
        logged_in_as = self._login(mobile, password)

        # LoginManager sets frappe.session.user to the User.name
        self.assertEqual(logged_in_as, user.name)

    def test_can_still_login_with_email(self):
        """Email-based login should still work."""
        mobile = "09125556677"
        password = "TestPassword123"

        user = self._make_user(mobile_no=mobile, password=password)
        user = frappe.get_doc("User", user.name)

        # Login with email
        logged_in_as = self._login(user.email, password)
        self.assertEqual(logged_in_as, user.name)

    def test_wrong_password_with_mobile_fails(self):
        """Login with correct mobile but wrong password should fail."""
        mobile = "09129998877"
        password = "CorrectPassword123"

        user = self._make_user(mobile_no=mobile, password=password)

        with self.assertRaises(AuthenticationError):
            self._login(mobile, "WrongPassword!")
