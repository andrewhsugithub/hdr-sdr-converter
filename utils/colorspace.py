import numpy as np

# === Gamut conversion matrices ===

MAT_709_TO_2020 = np.array(
    [
        [0.627402, 0.329292, 0.043306],
        [0.069095, 0.901368, 0.029537],
        [0.016394, 0.083234, 0.890372],
    ]
)

MAT_2020_TO_709 = np.array(
    [
        [1.660496, -0.587656, -0.072840],
        [-0.124547, 1.132895, -0.008348],
        [-0.018154, -0.100597, 1.118751],
    ]
)


def linear_709_to_2020(rgb: np.ndarray) -> np.ndarray:
    """Convert linear RGB from BT.709 to BT.2020 primaries."""
    h, w, c = rgb.shape
    flat = rgb.reshape(-1, 3)
    out = flat.dot(MAT_709_TO_2020.T)
    return out.reshape(h, w, c)


def linear_2020_to_709(rgb: np.ndarray) -> np.ndarray:
    """Convert linear RGB from BT.2020 to BT.709 primaries."""
    h, w, c = rgb.shape
    flat = rgb.reshape(-1, 3)
    out = flat.dot(MAT_2020_TO_709.T)
    return out.reshape(h, w, c)


# === YUV coefficients ===

# BT.709 3 Signal Format
KR_709 = 0.2126
KB_709 = 0.0722
KG_709 = 1.0 - KR_709 - KB_709  # 0.7152

# BT.2020 Table 4 and BT.2100 Table 6
KR_2020 = 0.2627
KB_2020 = 0.0593
KG_2020 = 1.0 - KR_2020 - KB_2020


def yuv_to_rgb_709(y: np.ndarray, u: np.ndarray, v: np.ndarray) -> np.ndarray:
    """YCbCr (BT.709 3 Signal Format) to RGB.

    Parameters:
        y, u, v: normalized [0-1], U/V centered at 0.5

    Returns:
        RGB array (H, W, 3)
    """
    u_shifted = u - 0.5
    v_shifted = v - 0.5

    # Conversion factors derived from BT.709 coefficients
    # 2(1 - KR_709) = 1.5748
    r = y + 1.5748 * v_shifted

    # 2KB_709 * (1 - KB_709)/KG_709 = 0.1873
    # 2KR_709 * (1 - KR_709)/KG_709 = 0.4681
    g = y - 0.1873 * u_shifted - 0.4681 * v_shifted

    # 2(1 - KB_709) = 1.8556
    b = y + 1.8556 * u_shifted

    return np.dstack((r, g, b))


def yuv_to_rgb_2020(y: np.ndarray, u: np.ndarray, v: np.ndarray) -> np.ndarray:
    """YCbCr (BT.2020 Table 4 and BT.2100 Table 6 Non-Constant Luminance) to RGB.

    Parameters:
        y, u, v: normalized [0-1], U/V centered at 0.5

    Returns:
        RGB array (H, W, 3)
    """
    u_s = u - 0.5
    v_s = v - 0.5

    # Conversion factors derived from BT.2020 coefficients
    # 2(1 - KR_2020) = 1.4746
    r = y + 1.4746 * v_s
    # 2KB_2020 * (1 - KB_2020)/KG_2020 = 0.16455
    # 2KR_2020 * (1 - KR_2020)/KG_2020 = 0.57135
    g = y - 0.16455 * u_s - 0.57135 * v_s
    # 2(1 - KB_2020) = 1.8814
    b = y + 1.8814 * u_s

    return np.dstack((r, g, b))


def rgb_to_yuv_709(rgb: np.ndarray):
    """RGB to YUV BT.709

    BT.709 3 Signal Format

    Parameters:
        rgb: RGB array (H, W, 3) normalized [0-1]

    Returns:
        y, u, v: normalized [0-1], U/V centered at 0.5
    """
    r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]

    y = KR_709 * r + KG_709 * g + KB_709 * b
    u = (b - y) / (2.0 * (1.0 - KB_709)) + 0.5
    v = (r - y) / (2.0 * (1.0 - KR_709)) + 0.5

    return y, u, v


def rgb_to_yuv_2020(rgb: np.ndarray):
    """RGB to YUV BT.2020

    BT.2020 Table 4 and BT.2100 Table 6 Non-Constant Luminance

    Parameters:
        rgb: RGB array (H, W, 3) normalized [0-1]

    Returns:
        y, u, v: normalized [0-1], U/V centered at 0.5
    """
    r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]

    y = KR_2020 * r + KG_2020 * g + KB_2020 * b
    u = (b - y) / (2.0 * (1.0 - KB_2020)) + 0.5
    v = (r - y) / (2.0 * (1.0 - KR_2020)) + 0.5

    return y, u, v
