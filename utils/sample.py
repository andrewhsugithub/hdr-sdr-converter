import cv2
import numpy as np


def upsample_chroma(u: np.ndarray, v: np.ndarray, width: int, height: int):
    """Upsample chroma from 4:2:0 to 4:4:4."""
    u_up = cv2.resize(u, (width, height), interpolation=cv2.INTER_LINEAR)
    v_up = cv2.resize(v, (width, height), interpolation=cv2.INTER_LINEAR)
    return u_up, v_up


def downsample_chroma(u: np.ndarray, v: np.ndarray):
    """Downsample chroma from 4:4:4 to 4:2:0."""
    h, w = u.shape[:2]
    u_down = cv2.resize(u, (w // 2, h // 2), interpolation=cv2.INTER_LINEAR)
    v_down = cv2.resize(v, (w // 2, h // 2), interpolation=cv2.INTER_LINEAR)
    return u_down, v_down
