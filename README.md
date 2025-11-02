
# invoice_kraken_ocr

**Handwritten Arabic OCR** for ERPNext using **Kraken** + **incremental learning**.

## Install
```bash
cd ~/frappe-bench
bench get-app https://github.com/<youruser>/<yourrepo>.git --branch main
bench --site emp123 install-app invoice_kraken_ocr
bench migrate
```

## Model
Put your base Arabic Kraken model at:
```
sites/emp123/private/files/kraken_models/base.mlmodel
```
The app will write fine-tuned model to:
```
sites/emp123/private/files/kraken_models/current.mlmodel
```

## DocTypes
- OCR Model Settings
- OCR Invoice Import
- OCR Invoice Item
- OCR Training Sample
