
frappe.ui.form.on('OCR Invoice Import', {
    refresh(frm) {
        if (!frm.is_new()) {
            frm.add_custom_button(__('Extract with Kraken'), () => {
                frappe.call({
                    method: "invoice_kraken_ocr.api.extract",
                    args: {name: frm.doc.name},
                }).then(() => frm.reload_doc());
            });
            frm.add_custom_button(__('Learn Now'), () => {
                frappe.call({
                    method: "invoice_kraken_ocr.api.learn_from_rows",
                    args: {name: frm.doc.name},
                }).then(() => frappe.show_alert({message:__('Stored training samples'), indicator:'green'}));
            });
            frm.add_custom_button(__('Retrain Model'), () => {
                frappe.call({
                    method: "invoice_kraken_ocr.api.retrain_model",
                }).then(r => {
                    frappe.msgprint(__('Model updated: {0}', [r.message.model]));
                }).catch(e => {
                    frappe.msgprint(__('Training failed: {0}', [e.message]));
                });
            });
        }
    }
});
