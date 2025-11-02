
from setuptools import setup, find_packages

setup(
    name="invoice_kraken_ocr",
    version="0.1.0",
    description="Kraken-based Arabic handwriting OCR for ERPNext with incremental learning",
    author="Paul Nabil",
    author_email="you@example.com",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "kraken>=4.3.15",
        "Pillow>=10.0.0",
        "numpy",
        "opencv-python-headless",
        "rapidfuzz>=3.8.0"
    ],
)
