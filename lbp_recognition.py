"""Compact, CPU-only LBP face descriptors for consent-based demo recognition."""
import cv2
import numpy as np

SIZE = 112
GRID = 8
FEATURE_SIZE = GRID * GRID * 256


def extract_lbp(face_rgb):
    """Return a normalized spatial LBP histogram (16384 values)."""
    if face_rgb is None or face_rgb.size == 0:
        raise ValueError("Empty face crop")
    if face_rgb.ndim == 3:
        gray = cv2.cvtColor(face_rgb, cv2.COLOR_RGB2GRAY)
    else:
        gray = face_rgb
    gray = cv2.resize(gray, (SIZE, SIZE), interpolation=cv2.INTER_AREA)
    gray = cv2.equalizeHist(gray)

    center = gray[1:-1, 1:-1]
    code = np.zeros(center.shape, dtype=np.uint8)
    bit = 0
    for dy, dx in [(-1, -1), (-1, 0), (-1, 1), (0, 1),
                   (1, 1), (1, 0), (1, -1), (0, -1)]:
        neighbor = gray[1 + dy:SIZE - 1 + dy, 1 + dx:SIZE - 1 + dx]
        code |= ((neighbor >= center).astype(np.uint8) << bit)
        bit += 1

    features = []
    height, width = code.shape
    for gy in range(GRID):
        y0, y1 = gy * height // GRID, (gy + 1) * height // GRID
        for gx in range(GRID):
            x0, x1 = gx * width // GRID, (gx + 1) * width // GRID
            hist = np.bincount(code[y0:y1, x0:x1].ravel(), minlength=256).astype(np.float32)
            hist /= max(float(hist.sum()), 1.0)
            features.extend(hist.tolist())
    return features


def compare_lbp(first, second):
    """Return chi-square distance; lower means more similar."""
    a = np.asarray(first, dtype=np.float32)
    b = np.asarray(second, dtype=np.float32)
    if a.size != FEATURE_SIZE or b.size != FEATURE_SIZE:
        raise ValueError("Invalid stored face descriptor")
    a = a.reshape(GRID * GRID, 256)
    b = b.reshape(GRID * GRID, 256)
    cell_distances = 0.5 * np.sum(((a - b) ** 2) / (a + b + 1e-8), axis=1)
    return float(np.mean(cell_distances))
