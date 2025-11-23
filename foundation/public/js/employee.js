// foundation/public/js/employee_mandatory.js

frappe.ui.form.on("Employee", {
    refresh(frm) {
        try {
            if (window.apply_mandatory_only) {
                // Example: keep same behavior as Customer for now
                window.apply_mandatory_only(frm, { show_on_edit: true });
            } else {
                console.warn("[Employee] apply_mandatory_only is not defined");
            }
        } catch (e) {
            console.error("[Employee] Error in mandatory-only logic:", e);
        }
    },
});
