// foundation/public/js/employee_mandatory.js

console.log("[employee_mandatory] file loaded");

frappe.ui.form.on("Employee", {
    refresh(frm) {
        console.log("[employee_mandatory] refresh for", frm.doctype, frm.doc.name);
    },
});
