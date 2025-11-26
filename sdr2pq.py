import os

import av
import cv2
import numpy as np

from utils.transfer import eotf_sdr, oetf_pq10
from utils.yuv_rgb_conv import rgb_to_yuv_rec2020_limited, yuv_to_rgb_rec709

INPUT_VIDEO = "test_sdr.mp4"


def linear_709_to_linear_2020(rgb_linear_709):
    """
    Rec.2087-0
    Converts Linear Rec.709 RGB to Linear Rec.2020 RGB.
    Math: [RGB2020] = [Inverse Matrix] * [RGB709]
    """
    # Inverse of the matrix used in the SDR conversion
    mat = np.array(
        [
            [0.627402, 0.329292, 0.043306],
            [0.069095, 0.901368, 0.029537],
            [0.016394, 0.083234, 0.890372],
        ]
    )

    h, w, c = rgb_linear_709.shape
    flat = rgb_linear_709.reshape(-1, 3)
    transformed = np.dot(flat, mat.T)
    return transformed.reshape(h, w, c)


def read_yuv_plane_8bit(plane, width, height):
    """
    Reads 8-bit plane (SDR input).
    """
    # Input is uint8
    raw_buffer = np.frombuffer(plane, np.uint8)
    stride = plane.line_size  # 1 byte per pixel
    raw_shaped = raw_buffer[: height * stride].reshape(height, stride)
    return raw_shaped[:, :width].astype(np.float32)


def write_yuv_plane_10bit(av_plane, data_uint16, width, height):
    """
    Writes 10-bit plane (HDR output).
    """
    # Output is uint16
    stride = av_plane.line_size // 2
    out_buffer = np.frombuffer(av_plane, np.uint16)
    out_view = out_buffer[: height * stride].reshape(height, stride)
    out_view[:, :width] = data_uint16


def process_video(input_path, output_path):
    # PyAV allows accessing the raw 10-bit planes, not like OpenCV, which only supports up to 8-bit.
    input_container = av.open(input_path)
    in_stream = input_container.streams.video[0]

    output_container = av.open(output_path, "w")

    # Output MUST be HEVC for HDR
    out_stream = output_container.add_stream("hevc", rate=in_stream.average_rate)
    out_stream.width = in_stream.width
    out_stream.height = in_stream.height
    out_stream.pix_fmt = "yuv420p10le"

    # Metadata for QuickTime/TVs
    out_stream.codec_context.codec_tag = "hvc1"

    print(f"Converting SDR -> PQ10: {input_path} -> {output_path}...")

    out_stream.options = {
        "crf": "20",
        "preset": "fast",
        "x265-params": "colorprim=bt2020:transfer=smpte2084:colormatrix=bt2020nc",
    }

    for frame in input_container.decode(in_stream):

        # --- 1. Read Input (8-bit SDR) ---
        y_float = read_yuv_plane_8bit(frame.planes[0], frame.width, frame.height)

        uv_w, uv_h = frame.width // 2, frame.height // 2
        u_float = read_yuv_plane_8bit(frame.planes[1], uv_w, uv_h)
        v_float = read_yuv_plane_8bit(frame.planes[2], uv_w, uv_h)

        # Standard SDR Video (Rec.709) ranges:
        # Y: 16 to 235
        # U/V: 16 to 240 (Centered at 128)

        # 1. Expand Luma (Y)
        # Formula: (Y - 16) / (235 - 16)
        y_norm = (y_float - 16.0) / 219.0

        # 2. Expand Chroma (U/V)
        # Formula: (UV - 128) / (240 - 16) * range + center
        # Assuming your yuv_to_rgb function expects 0.0-1.0 inputs:
        u_norm = (u_float - 16.0) / 224.0
        v_norm = (v_float - 16.0) / 224.0

        # 3. Clip to ensure clean 0.0-1.0 (removes "super-black" noise)
        y_norm = np.clip(y_norm, 0.0, 1.0)
        u_norm = np.clip(u_norm, 0.0, 1.0)
        v_norm = np.clip(v_norm, 0.0, 1.0)

        # Resize Chroma (Upscale to 4:4:4 for math)
        u_resized = cv2.resize(
            u_norm, (frame.width, frame.height), interpolation=cv2.INTER_LINEAR
        )
        v_resized = cv2.resize(
            v_norm, (frame.width, frame.height), interpolation=cv2.INTER_LINEAR
        )

        # --- 2. Color Pipeline ---

        # A. YUV (709) -> RGB (709 Gamma)
        rgb_gamma_709 = yuv_to_rgb_rec709(y_norm, u_resized, v_resized)

        # B. Remove Gamma (SDR -> Linear Light)
        # For file conversion, we set Lw=1.0 (Normalized) and Lb=0.0 (Ideal Black) to preserve contrast.
        rgb_linear_709 = eotf_sdr(rgb_gamma_709, Lw=1.0, Lb=0.0)

        # C. Convert Primaries (Rec.709 -> Rec.2020)
        # Note: This puts SDR colors into the larger container.
        # It does NOT artificially saturate them.
        rgb_linear_2020 = linear_709_to_linear_2020(rgb_linear_709)
        rgb_linear_2020 = np.maximum(rgb_linear_2020, 0.0)

        # D. Scale for PQ (Inverse Tone Map)
        # Map SDR White to 203 Nits (ITU Ref White)
        rgb_linear_pq_normalized = rgb_linear_2020 * (203.0 / 10000.0)

        # E. Apply PQ OETF (Linear -> PQ Signal)
        rgb_pq = oetf_pq10(rgb_linear_pq_normalized)

        # F. RGB -> YUV (Rec.2020 10-bit)
        y_final, u_final, v_final = rgb_to_yuv_rec2020_limited(rgb_pq)

        # --- 3. Write Output (10-bit HDR) ---
        out_frame = av.VideoFrame(
            width=out_stream.width, height=out_stream.height, format="yuv420p10le"
        )
        out_frame.pts = frame.pts
        out_frame.time_base = frame.time_base

        write_yuv_plane_10bit(
            out_frame.planes[0], y_final, out_stream.width, out_stream.height
        )
        write_yuv_plane_10bit(
            out_frame.planes[1], u_final, out_stream.width // 2, out_stream.height // 2
        )
        write_yuv_plane_10bit(
            out_frame.planes[2], v_final, out_stream.width // 2, out_stream.height // 2
        )

        for packet in out_stream.encode(out_frame):
            output_container.mux(packet)

    for packet in out_stream.encode():
        output_container.mux(packet)

    input_container.close()
    output_container.close()
    print("Done!")


# Usage
output_dir = "./output"
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "test_sdr2pq.mp4")
process_video(INPUT_VIDEO, output_path)
