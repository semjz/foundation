# apps/foundation/foundation/overrides/customer.py

from erpnext.selling.doctype.customer.customer import Customer as ERPNextCustomer
from foundation.general_hooks.canonical_id import set_canonical_id

class Customer(ERPNextCustomer):
    def autoname(self):
        # Call your canonical generator to fill custom_canonical_id
        set_canonical_id(self, method="autoname")

        # Use that as the actual document name
        if getattr(self, "custom_canonical_id", None):
            self.name = self.custom_canonical_id
        else:
            # Fallback to ERPNext default behavior if something is missing
            super().autoname()
