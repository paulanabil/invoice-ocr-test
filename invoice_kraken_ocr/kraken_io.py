
from io import BytesIO
from PIL import Image
import numpy as np
import cv2
import os
from kraken import binarization, rpred, pageseg, serialization

def _bytes_to_pil(img_bytes: bytes) -> Image.Image:
    arr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return Image.fromarray(img)

def preprocess_for_camera(img: Image.Image) -> Image.Image:
    return binarization.nlbin(img)

def load_model(path: str):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Kraken model not found: {path}")
    return serialization.load_any(path)

def predict_lines(img_bytes: bytes, model_path: str):
    pil = _bytes_to_pil(img_bytes)
    pil = preprocess_for_camera(pil)
    seg = pageseg.segment(pil)
    model = load_model(model_path)
    preds = rpred.rpred(model, pil, seg)
    lines = []
    for l in preds:
        text = l.prediction
        x1,y1,x2,y2 = l.bounds
        crop = pil.crop((x1,y1,x2,y2))
        output = BytesIO()
        crop.save(output, format="PNG")
        lines.append({"text": text, "crop": output.getvalue()})
    return lines

def train_model(base_model: str, output_path: str, training_pairs: list[tuple[str, str]]):
    # Placeholder: integrate kraken training pipeline or call kraken CLI with PAGE-XML/ALTO.
    # For now, this acts as a stub to keep the app structure valid.
    # Replace with actual kraken.training invocation in your environment.
    with open(output_path, "wb") as f:
        f.write(b"FAKE_MODEL")
    return output_path
