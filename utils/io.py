import numpy as np


def read_plane_8bit(plane, width: int, height: int) -> np.ndarray:
    """Read 8-bit YUV plane from PyAV frame."""
    raw = np.frombuffer(plane, np.uint8)
    stride = plane.line_size
    shaped = raw[: height * stride].reshape(height, stride)
    return shaped[:, :width].astype(np.float32)


def read_plane_10bit(plane, width: int, height: int) -> np.ndarray:
    """Read 10-bit YUV plane from PyAV frame."""
    raw = np.frombuffer(plane, np.uint16)
    stride = plane.line_size // 2
    shaped = raw[: height * stride].reshape(height, stride)
    return shaped[:, :width].astype(np.float32)


def write_plane_8bit(plane, data: np.ndarray, width: int, height: int):
    """Write 8-bit YUV plane to PyAV frame."""
    stride = plane.line_size
    out = np.frombuffer(plane, np.uint8)
    out[: height * stride].reshape(height, stride)[:, :width] = data.astype(np.uint8)


def write_plane_10bit(plane, data: np.ndarray, width: int, height: int):
    """Write 10-bit YUV plane to PyAV frame."""
    stride = plane.line_size // 2
    out = np.frombuffer(plane, np.uint16)
    out[: height * stride].reshape(height, stride)[:, :width] = data.astype(np.uint16)
