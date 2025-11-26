import numpy as np


def eotf_sdr(v, Lw=1.0, Lb=0.0, gamma=2.40):
    """SDR -> Linear Light

    BT.1886 (Annex 1 Reference electro-optical transfer function)

    Parameters:
        v: normalized video signal [0-1]
        Lw: white luminance (normalized, default 1.0, originally 100.0 cd/m² in BT.1886)
        Lb: black luminance (normalized, default 0.0, originally 0.1 cd/m² in BT.1886)
        gamma: power exponent (2.4)

    Returns:
        Linear light [0-1]
    """
    v = np.clip(v, 0, 1)

    Lw_g = Lw ** (1 / gamma)
    Lb_g = Lb ** (1 / gamma)

    a = (Lw_g - Lb_g) ** gamma
    b = Lb_g / (Lw_g - Lb_g)

    L = a * np.maximum(v + b, 0) ** gamma
    return L


def eotf_pq(v):
    """PQ Signal -> Linear Light

    BT.2100 (Table 4)

    Parameters:
        v: normalized video signal [0-1]

    Returns:
        Linear light [0-1] (where 1.0 = 10000 nits)
    """
    m1 = 2610 / 16384.0  # 0.1593017578125
    m2 = 2523 / 4096.0 * 128  # 78.84375
    c1 = 3424 / 4096.0  # 0.8359375
    c2 = 2413 / 4096.0 * 32  # 18.8515625
    c3 = 2392 / 4096.0 * 32  # 18.6875

    v = np.clip(v, 0, 1)
    v_p = np.maximum(v ** (1.0 / m2) - c1, 0)
    denom = c2 - c3 * v ** (1.0 / m2)
    L = (v_p / denom) ** (1.0 / m1)

    return np.clip(L, 0, 1)


def eotf_hlg(v):
    """HLG Signal -> Linear Light

    BT.2100 (Table 5)

    Parameters:
        v: normalized video signal [0-1]

    Returns:
        Linear light [0-1] (where 1.0 = 1000 nits nominal)
    """
    a = 0.17883277
    b = 1 - 4 * a
    c = 0.5 - a * np.log(4 * a)

    v = np.clip(v, 0, 1)
    L = np.where(v <= 0.5, (v**2) / 3.0, (np.exp((v - c) / a) + b) / 12.0)
    return np.clip(L, 0, 1)


def oetf_sdr(L):
    """Linear Light -> SDR Signal

    BT.709 (1 Opto-electronic conversion)

    Parameters:
        L: linear light [0-1]

    Returns:
        Video signal [0-1]
    """
    L = np.clip(L, 0, 1)
    return np.where(L < 0.018, 4.5 * L, 1.099 * (L**0.45) - 0.099)


def oetf_pq(L):
    """Linear Light -> PQ Signal

    BT.2100 (Table 4)

    Parameters:
        L: linear light [0-1] (where 1.0 = 10000 nits)

    Returns:
        Video signal [0-1]
    """
    m1 = 2610 / 16384.0  # 0.1593017578125
    m2 = 2523 / 4096.0 * 128  # 78.84375
    c1 = 3424 / 4096.0  # 0.8359375
    c2 = 2413 / 4096.0 * 32  # 18.8515625
    c3 = 2392 / 4096.0 * 32  # 18.6875

    L = np.clip(L, 0, 1)
    L_p = L**m1
    return ((c1 + c2 * L_p) / (1 + c3 * L_p)) ** m2


def oetf_hlg(L):
    """Linear Light -> HLG Signal

    BT.2100 (Table 5)

    Parameters:
        L: linear light [0-1] (where 1.0 = 1000 nits nominal)

    Returns:
        Video signal [0-1]
    """
    a = 0.17883277
    b = 1.0 - (4.0 * a)  # 0.28466892
    c = 0.5 - a * np.log(4.0 * a)  # 0.55991073

    hlg_out = np.zeros_like(L)

    # 0 <= E <= 1/12
    mask_low = L <= (1.0 / 12.0)
    hlg_out[mask_low] = np.sqrt(3.0 * L[mask_low])
    # E > 1/12
    mask_high = ~mask_low
    val_high = np.maximum(L[mask_high], 1e-9)
    hlg_out[mask_high] = a * np.log(12.0 * val_high - b) + c

    return hlg_out
