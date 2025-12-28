frappe.ui.form.on("Employee", {
  refresh(frm) {
    // Run after other handlers / ajax
    frappe.after_ajax(() => {
      setTimeout(() => {
        const f = frm.fields_dict.naming_series;
        if (!f) return;

        frm.set_df_property("naming_series", "reqd", 0);
        frm.set_df_property("naming_series", "hidden", 1);
        frm.toggle_display("naming_series", false);

        if (f.wrapper) {
          f.wrapper.style.display = "none";
        }
      }, 300);
    });
  },
});
