
import os, tempfile
import frappe
from frappe import _
from .kraken_io import predict_lines, train_model
from .parser import parse_items

def _settings():
    return frappe.get_single("OCR Model Settings")

@frappe.whitelist()
def extract(name: str):
    doc = frappe.get_doc("OCR Invoice Import", name)
    if not doc.image:
        frappe.throw(_("Please attach an invoice image first."))

    file = frappe.get_doc("File", {"file_url": doc.image})
    content = file.get_content()

    cfg = _settings()
    model_path = frappe.get_site_path(cfg.current_model_path or cfg.base_model_path)
    lines = predict_lines(content, model_path)

    raw = "\n".join([l["text"] for l in lines])
    doc.raw_text = raw

    # Basic parse
    rows = []
    parsed = parse_items(raw)
    for i, it in enumerate(parsed):
        crop_bytes = lines[i]["crop"] if i < len(lines) else None
        row = {
            "line_text": it.get("name"),
            "corrected_text": it.get("name"),
            "qty": it.get("qty"),
            "rate": it.get("rate"),
            "amount": it.get("amount"),
        }
        if crop_bytes:
            fname = frappe.generate_hash(length=8) + ".png"
            fdoc = frappe.get_doc({
                "doctype": "File",
                "file_name": fname,
                "is_private": 1,
                "content": crop_bytes
            }).insert(ignore_permissions=True)
            row["line_image"] = fdoc.file_url
        rows.append(row)

    doc.set("items", rows)
    doc.status = "Extracted"
    doc.save()
    return {"ok": True, "lines": len(lines)}

@frappe.whitelist()
def learn_from_rows(name: str):
    doc = frappe.get_doc("OCR Invoice Import", name)
    for row in doc.items or []:
        if row.line_image and row.corrected_text:
            frappe.get_doc({
                "doctype": "OCR Training Sample",
                "image": row.line_image,
                "label": row.corrected_text
            }).insert(ignore_permissions=True)
    return {"ok": True}

@frappe.whitelist()
def retrain_model():
    cfg = _settings()
    base = frappe.get_site_path(cfg.base_model_path)
    out_dir = frappe.get_site_path(cfg.output_dir)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "current.mlmodel")

    samples = frappe.get_all("OCR Training Sample", fields=["image","label"])
    if len(samples) < (cfg.min_samples_to_train or 50):
        frappe.throw(_("Not enough training samples yet."))

    pairs = []
    with tempfile.TemporaryDirectory() as td:
        for i, s in enumerate(samples):
            imgf = os.path.join(td, f"line_{i}.png")
            labf = os.path.join(td, f"line_{i}.txt")
            fdoc = frappe.get_doc("File", {"file_url": s["image"]})
            with open(imgf, "wb") as f:
                f.write(fdoc.get_content())
            with open(labf, "w", encoding="utf-8") as f:
                f.write(s["label"] or "")
            pairs.append((imgf, labf))
        from .kraken_io import train_model
        train_model(base, out_path, pairs)

    cfg.current_model_path = cfg.output_dir.rstrip("/") + "/current.mlmodel"
    cfg.save()
    return {"ok": True, "model": cfg.current_model_path}

@frappe.whitelist()
def create_purchase_invoice(name: str):
    doc = frappe.get_doc("OCR Invoice Import", name)
    if doc.party_type != "Supplier":
        frappe.throw(_("Party Type must be Supplier"))
    if not doc.party:
        frappe.throw(_("Please set Supplier in Party"))
    pi = frappe.new_doc("Purchase Invoice")
    pi.supplier = doc.party
    if doc.posting_date:
        pi.posting_date = doc.posting_date
    for row in doc.items or []:
        if not row.item_code:
            continue
        pi.append("items", {"item_code": row.item_code, "qty": row.qty or 1, "rate": row.rate or 0})
    pi.insert(ignore_permissions=True)
    return {"ok": True, "purchase_invoice": pi.name}

@frappe.whitelist()
def create_sales_invoice(name: str):
    doc = frappe.get_doc("OCR Invoice Import", name)
    if doc.party_type != "Customer":
        frappe.throw(_("Party Type must be Customer"))
    if not doc.party:
        frappe.throw(_("Please set Customer in Party"))
    si = frappe.new_doc("Sales Invoice")
    si.customer = doc.party
    if doc.posting_date:
        si.posting_date = doc.posting_date
    for row in doc.items or []:
        if not row.item_code:
            continue
        si.append("items", {"item_code": row.item_code, "qty": row.qty or 1, "rate": row.rate or 0})
    si.insert(ignore_permissions=True)
    return {"ok": True, "sales_invoice": si.name}
