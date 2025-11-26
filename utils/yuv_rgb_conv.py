import cv2
import numpy as np


def yuv_to_rgb_rec709(y, u, v):
    """
    Converts YUV (Rec.709) to RGB.
    Expects normalized inputs [0.0-1.0].
    """
    # Standard BT.709 conversion
    # U/V are centered at 0.5
    u_shifted = u - 0.5
    v_shifted = v - 0.5

    r = y + 1.5748 * v_shifted
    g = y - 0.1873 * u_shifted - 0.4681 * v_shifted
    b = y + 1.8556 * u_shifted

    return np.dstack((r, g, b))


def yuv_to_rgb_rec2020(y, u, v):
    """
    Converts YUV (Rec.2020) to RGB.
    Expects normalized inputs [0.0-1.0].
    """
    # Rec. 2020 NCL (Non-Constant Luminance) Matrix
    # R = Y + 1.4746 * (V - 0.5)
    # G = Y - 0.16455 * (U - 0.5) - 0.57135 * (V - 0.5)
    # B = Y + 1.8814 * (U - 0.5)

    # Adjust UV range (video range usually centers at 0.5)
    u_shifted = u - 0.5
    v_shifted = v - 0.5

    r = y + (1.4746 * v_shifted)
    g = y - (0.16455 * u_shifted) - (0.57135 * v_shifted)
    b = y + (1.8814 * u_shifted)

    return np.dstack((r, g, b))


def rgb_to_yuv_rec2020_limited(rgb_hlg):
    """
    Converts RGB to YUV using Rec. 2020-2 Table 4 Rec. 2100-3 Table 6 NCL Matrix (for HDR/HLG).
    Output is 10-bit Limited Range (64-940 for Y, 64-960 for UV in 10-bit scale).
    """
    height, width, _ = rgb_hlg.shape

    # Rec. 2020 Coefficients
    Kr = 0.2627
    Kb = 0.0593
    Kg = 1.0 - Kr - Kb  # 0.6780

    r = rgb_hlg[:, :, 0]
    g = rgb_hlg[:, :, 1]
    b = rgb_hlg[:, :, 2]

    y = Kr * r + Kg * g + Kb * b
    cb = 0.5 * (b - y) / (1.0 - Kb)
    cr = 0.5 * (r - y) / (1.0 - Kr)

    # Scaling to 10-bit Limited Range
    # 10-bit Range: 0-1023
    # Y: 64 to 940 (Range 876)
    # UV: 64 to 960 (Range 896, centered at 512)

    y_10 = (876.0 * y) + 64.0
    cb_10 = (896.0 * cb) + 512.0
    cr_10 = (896.0 * cr) + 512.0

    # Clip to valid 10-bit range
    y_final = np.clip(y_10, 0, 1023).astype(np.uint16)
    cb_final = np.clip(cb_10, 0, 1023).astype(np.uint16)
    cr_final = np.clip(cr_10, 0, 1023).astype(np.uint16)

    # Resize Chroma (4:4:4 -> 4:2:0)
    cb_half = cv2.resize(
        cb_final, (width // 2, height // 2), interpolation=cv2.INTER_LINEAR
    )
    cr_half = cv2.resize(
        cr_final, (width // 2, height // 2), interpolation=cv2.INTER_LINEAR
    )

    return y_final, cb_half, cr_half


def rgb_to_yuv420_limited(rgb_gamma):
    """
    Converts Gamma-Encoded RGB to YUV420p (Limited Range/TV).
    Implements m=bt709, r=tv, and format=yuv420p.
    """
    height, width, _ = rgb_gamma.shape

    # --- 1. Matrix Conversion (m=bt709) ---
    # Coefficients for Rec.709-6 Table 3
    Kr = 0.2126
    Kb = 0.0722
    Kg = 1.0 - Kr - Kb  # 0.7152

    r = rgb_gamma[:, :, 0]
    g = rgb_gamma[:, :, 1]
    b = rgb_gamma[:, :, 2]

    y = Kr * r + Kg * g + Kb * b
    # Cb = 0.5 * (B - Y) / (1 - Kb)
    cb = 0.5 * (b - y) / (1.0 - Kb)
    # Cr = 0.5 * (R - Y) / (1 - Kr)
    cr = 0.5 * (r - y) / (1.0 - Kr)

    # --- 2. Range Scaling (r=tv) ---
    # BT. 601-7 2.5.3 Quantization, BT. 2020-2 Table 5
    # We are targeting 8-bit output (0-255)
    # Y maps 0.0-1.0 to 16-235
    # Cb/Cr maps -0.5 to +0.5 to 16-240 (centered at 128)

    y_tv = (219.0 * y) + 16.0
    cb_tv = (224.0 * cb) + 128.0
    cr_tv = (224.0 * cr) + 128.0

    # Clip to valid 8-bit range
    y_final = np.clip(y_tv, 0, 255).astype(np.uint8)
    cb_final = np.clip(cb_tv, 0, 255).astype(np.uint8)
    cr_final = np.clip(cr_tv, 0, 255).astype(np.uint8)

    # --- 3. Chroma Subsampling (format=yuv420p) ---
    # 4:2:0 means Chroma is half resolution of Luma.
    # We resize Cb and Cr to half width and half height.
    # INTER_LINEAR is standard for downscaling.

    cb_half = cv2.resize(
        cb_final, (width // 2, height // 2), interpolation=cv2.INTER_LINEAR
    )
    cr_half = cv2.resize(
        cr_final, (width // 2, height // 2), interpolation=cv2.INTER_LINEAR
    )

    return y_final, cb_half, cr_half
