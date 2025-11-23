// foundation/public/js/mandatory_only.js

console.log("[mandatory_only] file loaded");

function apply_mandatory_only(frm, { show_on_edit = true } = {}) {
    if (!frm || !frm.meta || !frm.meta.fields) {
        console.warn("[mandatory_only] frm.meta.fields missing");
        return;
    }

    const is_new = frm.is_new();

    frm.meta.fields.forEach(df => {
        if (['Section Break', 'Column Break', 'Tab Break'].includes(df.fieldtype)) {
            return;
        }

        const is_required = !!df.reqd;

        if (is_new) {
            // new doc: only show mandatory fields
            frm.toggle_display(df.fieldname, is_required);
        } else if (show_on_edit) {
            // edit: show everything
            frm.toggle_display(df.fieldname, true);
        }
    });

    console.log(
        `[mandatory_only] applied on ${frm.doctype} (new=${is_new}, show_on_edit=${show_on_edit})`
    );
}

// Attach to both doctypes in one file
["Customer", "Employee"].forEach(doctype => {
    frappe.ui.form.on(doctype, {
        refresh(frm) {
            console.log(`[mandatory_only] refresh for ${doctype}`, frm.doc.name);
            apply_mandatory_only(frm, { show_on_edit: true });
        },
    });
});
