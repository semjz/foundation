// foundation/public/js/customer_mandatory.js

console.log("[customer_mandatory] file loaded");

frappe.ui.form.on("Customer", {
    refresh(frm) {
        console.log("[customer_mandatory] refresh for", frm.doctype, frm.doc.name);
    },
});
