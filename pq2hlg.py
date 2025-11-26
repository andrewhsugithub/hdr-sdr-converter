import os

import av
import cv2
import numpy as np

from utils.transfer import eotf_pq10, oetf_hlg
from utils.yuv_rgb_conv import rgb_to_yuv_rec2020_limited, yuv_to_rgb_rec2020

INPUT_VIDEO = "test_pq.mp4"


def read_yuv_plane(plane, width, height):
    """
    Safely reads a PyAV plane into a numpy array, handling stride/padding.
    """
    # 1. Access raw buffer as uint16 (since it's 10-bit data)
    # Note: 'yuv420p10le' uses 2 bytes per pixel
    raw_buffer = np.frombuffer(plane, np.uint16)

    # 2. Calculate Stride (pixels per row in the buffer)
    # plane.line_size is in bytes. Divide by 2 for uint16.
    stride = plane.line_size // 2

    # 3. Reshape to (Height, Stride) to separate rows
    # Note: The buffer might be slightly larger than height*stride due to strict padding
    # We slice raw_buffer to fit exactly height * stride
    raw_shaped = raw_buffer[: height * stride].reshape(height, stride)

    # 4. Crop the valid width (ignore padding on the right)
    return raw_shaped[:, :width].astype(np.float32)


def write_yuv_plane_10bit(av_plane, data_uint16, width, height):
    """
    Writes 10-bit (uint16) data into a PyAV plane.
    """
    # 1. Get stride (in 2-byte elements)
    # line_size is bytes, so divide by 2
    stride = av_plane.line_size // 2

    # 2. Get buffer as uint16
    out_buffer = np.frombuffer(av_plane, np.uint16)

    # 3. Reshape view to match stride
    out_view = out_buffer[: height * stride].reshape(height, stride)

    # 4. Write data
    out_view[:, :width] = data_uint16


def process_video(input_path, output_path):
    # PyAV allows accessing the raw 10-bit planes, not like OpenCV, which only supports up to 8-bit.
    input_container = av.open(input_path)
    in_stream = input_container.streams.video[0]

    output_container = av.open(output_path, "w")

    out_stream = output_container.add_stream("hevc", rate=in_stream.average_rate)
    out_stream.width = in_stream.width
    out_stream.height = in_stream.height
    out_stream.pix_fmt = "yuv420p10le"

    out_stream.codec_context.codec_tag = "hvc1"

    out_stream.options = {
        "crf": "20",
        "preset": "fast",
        "x265-params": "colorprim=bt2020:transfer=arib-std-b67:colormatrix=bt2020nc",
    }

    print(f"Converting PQ -> HLG: {input_path} -> {output_path}")

    for frame in input_container.decode(in_stream):

        # --- 1. Read Input (Same as before) ---
        y_float = read_yuv_plane(frame.planes[0], frame.width, frame.height)

        uv_w, uv_h = frame.width // 2, frame.height // 2
        u_float = read_yuv_plane(frame.planes[1], uv_w, uv_h)
        v_float = read_yuv_plane(frame.planes[2], uv_w, uv_h)

        # Normalize 10-bit input
        y_norm = y_float / 1023.0
        u_norm = u_float / 1023.0
        v_norm = v_float / 1023.0

        # Resize Chroma up
        u_resized = cv2.resize(
            u_norm, (frame.width, frame.height), interpolation=cv2.INTER_LINEAR
        )
        v_resized = cv2.resize(
            v_norm, (frame.width, frame.height), interpolation=cv2.INTER_LINEAR
        )

        # --- 2. Color Pipeline ---

        # A. YUV -> RGB Rec.2020 (Same as before)
        rgb_nonlinear = yuv_to_rgb_rec2020(y_norm, u_resized, v_resized)

        # B. Linearize PQ -> Nits
        rgb_linear_nits = eotf_pq10(rgb_nonlinear) * 10000.0

        # C. Normalize for HLG
        # HLG is relative. We must map "Nits" to 0.0-1.0.
        # Standard: 1000 nits = 1.0 signal.
        rgb_linear_normalized = rgb_linear_nits / 1000.0

        # Note on Clipping: HLG technically supports up to 12.0 (super bright),
        # but the OETF math expects roughly 0-1 range for the standard curve.
        # Usually, we clip or soft-roll to 1.0 (1000 nits) for broadcast safety,
        # or leave slight headroom. Let's clip to 1.0 for standard safety.
        rgb_linear_normalized = np.clip(rgb_linear_normalized, 0.0, 1.0)

        # E. Apply HLG OETF
        rgb_hlg = oetf_hlg(rgb_linear_normalized)

        # F. RGB -> YUV Rec.2020 (10-bit)
        y_final, u_final, v_final = rgb_to_yuv_rec2020_limited(rgb_hlg)

        # --- 3. Write Output (10-bit) ---
        out_frame = av.VideoFrame(
            width=out_stream.width, height=out_stream.height, format="yuv420p10le"
        )
        out_frame.pts = frame.pts
        out_frame.time_base = frame.time_base

        # Use the 10-bit writer!
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
output_path = os.path.join(output_dir, "test_pq2hlg.mp4")
process_video(INPUT_VIDEO, output_path)
