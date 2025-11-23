// foundation/public/js/customer_mandatory.js

frappe.ui.form.on("Customer", {
    refresh(frm) {
        try {
            if (window.apply_mandatory_only) {
                window.apply_mandatory_only(frm, { show_on_edit: true });
            } else {
                console.warn("[Customer] apply_mandatory_only is not defined");
            }
        } catch (e) {
            console.error("[Customer] Error in mandatory-only logic:", e);
        }
    },
});
