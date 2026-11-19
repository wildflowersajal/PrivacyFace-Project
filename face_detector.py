"""Lightweight face detection using OpenCV Haar cascades."""
import base64
import io
from typing import List, Tuple

import cv2
import numpy as np
from PIL import Image


class FaceDetector:
    """Low-memory face detector suitable for small CPU instances."""

    def __init__(self, min_detection_confidence: float = 0.7):
        cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        self.detector = cv2.CascadeClassifier(cascade_path)
        if self.detector.empty():
            raise RuntimeError("Could not load OpenCV Haar face detector")
        self.min_neighbors = 5

    def decode_image(self, base64_image: str) -> np.ndarray:
        if "," in base64_image:
            base64_image = base64_image.split(",", 1)[1]
        image_bytes = base64.b64decode(base64_image)
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        return np.asarray(image)

    def detect_faces(self, image: np.ndarray) -> List[Tuple[np.ndarray, dict]]:
        if image.ndim == 2:
            gray = image
            rgb = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        elif image.shape[2] == 4:
            rgb = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
            gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
        else:
            rgb = image
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

        h, w = gray.shape[:2]
        scale = min(1.0, 640.0 / max(h, w))
        if scale < 1.0:
            small = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
        else:
            small = gray

        boxes = self.detector.detectMultiScale(
            small, scaleFactor=1.1, minNeighbors=self.min_neighbors,
            minSize=(40, 40)
        )

        faces = []
        for sx, sy, sw, sh in boxes:
            x, y = int(sx / scale), int(sy / scale)
            width, height = int(sw / scale), int(sh / scale)
            pad_x, pad_y = int(width * 0.25), int(height * 0.25)
            x0, y0 = max(0, x - pad_x), max(0, y - pad_y)
            x1, y1 = min(w, x + width + pad_x), min(h, y + height + pad_y)
            crop = rgb[y0:y1, x0:x1]
            if crop.size:
                faces.append((crop, {
                    "x": x0, "y": y0, "width": x1 - x0, "height": y1 - y0
                }))
        return faces

    def detect_from_base64(self, base64_image: str):
        return self.detect_faces(self.decode_image(base64_image))
