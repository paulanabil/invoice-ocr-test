
app_name = "invoice_kraken_ocr"
app_title = "Invoice Kraken OCR"
app_publisher = "You"
app_description = "Handwritten Arabic OCR with Kraken, incremental learning, ERPNext integration"
app_email = "you@example.com"
app_license = "MIT"

# Include minimal asset built from build.json (keeps esbuild stable)
app_include_js = ["invoice_kraken_ocr.bundle.js"]

scheduler_events = {
    "daily": [
        "invoice_kraken_ocr.train.schedule_daily_retrain"
    ]
}
