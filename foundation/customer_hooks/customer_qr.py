import frappe
import qrcode
from io import BytesIO
from frappe.utils.file_manager import save_file


def ensure_customer_qr_code(doc, method=None):
    """Create QR code for Customer canonical_id and set qr_code field."""
    # Make sure we actually have a canonical_id
    if not getattr(doc, "canonical_id", None):
        return

    # Generate QR image in memory
    qr = qrcode.QRCode(border=2)
    qr.add_data(doc.custom_canonical_id)
    qr.make(fit=True)
    img = qr.make_image()

    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    # Save as File attached to this Customer
    file_name = f"Customer-{doc.name}-QR.png"
    file_doc = save_file(
        file_name,
        buffer.getvalue(),
        doc.doctype,
        doc.name,
        is_private=0,  # or 1 if you want it private
    )

    # Update the qr_code field (Image / Attach) on Customer
    frappe.db.set_value(doc.doctype, doc.name, "custom_qr_code", file_doc.file_url)
