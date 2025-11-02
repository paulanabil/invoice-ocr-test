
import frappe
from frappe.utils.background_jobs import enqueue

def schedule_daily_retrain():
    try:
        cfg = frappe.get_single("OCR Model Settings")
        if not cfg.enabled_daily_train:
            return
        enqueue(train_now, queue="long", job_name="kraken_retrain_daily")
    except Exception:
        frappe.log_error("Kraken OCR daily retrain scheduler error")

@frappe.whitelist()
def train_now():
    from .api import retrain_model
    return retrain_model()
