import numpy as np

# === 8-bit limited range (BT.709 4 Digital Representation) ===


def normalize_8bit(y: np.ndarray, u: np.ndarray, v: np.ndarray):
    """Normalize 8-bit YUV to [0-1].

    Standard SDR Video (BT.709 4 Digital Representation) ranges: Y: 16-235, UV: 16-240
    """
    y_norm = np.clip((y - 16.0) / 219.0, 0.0, 1.0)
    u_norm = np.clip((u - 16.0) / 224.0, 0.0, 1.0)
    v_norm = np.clip((v - 16.0) / 224.0, 0.0, 1.0)
    return y_norm, u_norm, v_norm


def quantize_8bit(y: np.ndarray, u: np.ndarray, v: np.ndarray):
    """Quantize normalized [0-1] to 8-bit YUV.

    Standard SDR Video (Rec.709 4 Digital Representation) ranges: Y: 16-235, UV: 16-240
    """
    y_out = np.clip(np.round(y * 219.0 + 16.0), 16, 235).astype(np.uint8)
    u_out = np.clip(np.round(u * 224.0 + 16.0), 16, 240).astype(np.uint8)
    v_out = np.clip(np.round(v * 224.0 + 16.0), 16, 240).astype(np.uint8)
    return y_out, u_out, v_out


# === 10-bit limited range (BT.2020 Table 5 and BT.2100 Table 9 Narrow range) ===


def normalize_10bit(y: np.ndarray, u: np.ndarray, v: np.ndarray):
    """Normalize 10-bit YUV to [0-1].

    Standard PQ/HLG Video (BT.2020 Table 5 and BT.2100 Table 9 Narrow range) ranges: Y: 64-940, UV: 64-960
    """
    y_norm = np.clip((y - 64.0) / 876.0, 0.0, 1.0)
    u_norm = np.clip((u - 64.0) / 896.0, 0.0, 1.0)
    v_norm = np.clip((v - 64.0) / 896.0, 0.0, 1.0)
    return y_norm, u_norm, v_norm


def quantize_10bit(y: np.ndarray, u: np.ndarray, v: np.ndarray):
    """Quantize normalized [0-1] to 10-bit limited range.

    Standard PQ/HLG Video (BT.2020 Table 5 and BT.2100 Table 9 Narrow range) ranges: Y: 64-940, UV: 64-960
    """
    y_out = np.clip(np.round(y * 876.0 + 64.0), 64, 940).astype(np.uint16)
    u_out = np.clip(np.round(u * 896.0 + 64.0), 64, 960).astype(np.uint16)
    v_out = np.clip(np.round(v * 896.0 + 64.0), 64, 960).astype(np.uint16)
    return y_out, u_out, v_out
