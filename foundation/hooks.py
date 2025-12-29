# ------------------------------------------------------------
# App Meta
# ------------------------------------------------------------

app_name = "foundation"
app_title = "Foundation"
app_publisher = "Saman Malakjan"
app_description = "This app is the foundation and should be installed before all apps"
app_email = "saman.malakjan@gmail.com"
app_license = "mit"

# Ensure ERPNext is installed before this app
required_apps = ["erpnext"]

# ------------------------------------------------------------
# Constants / Shared Config
# ------------------------------------------------------------

# Core doctypes that this app customizes
edited_core_doctypes = ["Employee", "Customer", "Company", "Contract", "Sales Invoice"]

# Roles we care about as fixtures
# NOTE: include both "Ops Manger" and "Ops Manager" to be safe while you migrate naming.
role_names = [
    "Customer",
    "Employee",
    "Ops Manager",  # correct spelling
    "Finance",
    "Letter Generator",
]


# ------------------------------------------------------------
# Client Scripts
# ------------------------------------------------------------

doctype_js = {
    # Hide naming_series on Employee form (ensure the file exists in this path)
    "Employee": "public/js/employee_hide_series.js",
}


# ------------------------------------------------------------
# Doc Events
# ------------------------------------------------------------

standard_queries = {
    "Territory": "foundation.territory_hooks.query.territory_link_query",
}


doc_events = {
    "Employee": {
        "before_insert": [
            "foundation.employee_hooks.identity.enforce_business_keys",
            "foundation.employee_hooks.numbering.assign_employee_display_number",
            "foundation.employee_hooks.org_role.require_org_role_fields",
            "foundation.general_hooks.canonical_id.set_canonical_id",
        ],
        "validate": [
            "foundation.employee_hooks.org_role.require_org_role_fields",
            "foundation.employee_hooks.identity.recheck_uniqueness",
            "foundation.employee_hooks.payroll.compute_payroll_flags",
            "foundation.jalali_hooks.conversion.employee_validate",
        ],
        "before_save": [
            "foundation.employee_hooks.immutability.lock_immutable_identifiers",
            # "foundation.employee_hooks.id_scan.enforce_employee_national_id_attachment_policy",
        ],
        "after_insert": [
            "foundation.employee_hooks.create_user.create_user_and_permission",
            "foundation.employee_hooks.checklist.employee_after_insert",
        ],
    },
    "Customer": {
        "before_insert": "foundation.general_hooks.canonical_id.set_canonical_id",
        "after_insert": [
            "foundation.customer_hooks.portal.ensure_user_and_permission",
            "foundation.customer_hooks.customer_qr.ensure_customer_qr_code",
        ],
        "validate": [
            "foundation.customer_hooks.customer_business_rules.validate_customer_business_rules",
            # "foundation.customer_hooks.customer_tier_rules.enforce_customer_tier_rules",
        ],
        "on_update": "foundation.customer_hooks.customer_qr.ensure_customer_qr_code",
    },
    "File": {
        "before_insert": "foundation.file_hooks.national_id_scan.apply_employee_national_id_file_policy_on_create",
        "after_insert": "foundation.employee_hooks.checklist.file_after_insert",
        "after_delete": "foundation.employee_hooks.checklist.file_after_delete",
    },
}


# ------------------------------------------------------------
# Fixtures
# ------------------------------------------------------------
# WARNING:
# - Custom Field / Property Setter / Custom DocPerm for edited_core_doctypes
#   will be applied on every migrate. Clean bad ones BEFORE export-fixtures.
# - Workspace / Gender fixtures will override manual changes on other sites.

fixtures = [
    # All Workspaces (consider adding filters later if you want only your own)
    "Workspace",

    # Custom Fields for edited core doctypes
    {
        "dt": "Custom Field",
        "filters": [
            ["dt", "in", edited_core_doctypes],
        ],
    },

    # Property Setters for edited core doctypes
    {
        "dt": "Property Setter",
        "filters": [
            ["doc_type", "in", edited_core_doctypes],
        ],
    },

    # Custom DocPerm (permissions overrides) for edited core doctypes
    {
        "dt": "Custom DocPerm",
        "filters": [
            ["parent", "in", edited_core_doctypes],
        ],
    },

    {
        "dt": "Custom DocPerm",
        "filters": [
            ["role", "=", "CEO"],
        ],
    },


    # Client Scripts bound to edited core doctypes
    {
        "dt": "Client Script",
        "filters": [
            ["dt", "in", edited_core_doctypes],
        ],
    },

    # Server Scripts bound to edited core doctypes
    {
        "dt": "Server Script",
        "filters": [
            ["reference_doctype", "in", edited_core_doctypes],
        ],
    },

    # Roles used by this app
    {
        "dt": "Role",
        "filters": [
            ["role_name", "in", role_names],
        ],
    },
]




# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "foundation",
# 		"logo": "/assets/foundation/logo.png",
# 		"title": "foundation",
# 		"route": "/foundation",
# 		"has_permission": "foundation.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/foundation/css/foundation.css"
# app_include_js = "/assets/foundation/js/foundation.js"

# include js, css files in header of web template
# web_include_css = "/assets/foundation/css/foundation.css"
# web_include_js = "/assets/foundation/js/foundation.js"

# include custom scss in every webCustomer Site theme (without file extension ".scss")
# webCustomer Site_theme_scss = "foundation/public/scss/webCustomer Site"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "foundation/public/icons.svg"

# Home Pages
# ----------

# application home page (will override WebCustomer Site Settings)
# home_page = "login"

# webCustomer Site user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# webCustomer Site_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "foundation.utils.jinja_methods",
# 	"filters": "foundation.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "foundation.install.before_install"
# after_install = "foundation.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "foundation.uninstall.before_uninstall"
# after_uninstall = "foundation.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "foundation.utils.before_app_install"
# after_app_install = "foundation.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "foundation.utils.before_app_uninstall"
# after_app_uninstall = "foundation.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "foundation.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"foundation.tasks.all"
# 	],
# 	"daily": [
# 		"foundation.tasks.daily"
# 	],
# 	"hourly": [
# 		"foundation.tasks.hourly"
# 	],
# 	"weekly": [
# 		"foundation.tasks.weekly"
# 	],
# 	"monthly": [
# 		"foundation.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "foundation.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "foundation.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "foundation.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["foundation.utils.before_request"]
# after_request = ["foundation.utils.after_request"]

# Job Events
# ----------
# before_job = ["foundation.utils.before_job"]
# after_job = ["foundation.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"foundation.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

