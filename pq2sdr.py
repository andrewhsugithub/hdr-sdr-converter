import os

import av
import cv2
import numpy as np

from utils.transfer import eotf_pq10, oetf_sdr
from utils.yuv_rgb_conv import rgb_to_yuv420_limited, yuv_to_rgb_rec2020

INPUT_VIDEO = "test_pq.mp4"


def linear_2020_to_linear_709(rgb_linear_2020):
    """
    Rec.2087-0
    Converts Linear Rec.2020 RGB to Linear Rec.709 RGB.
    Math: [RGB709] = [Matrix] * [RGB2020]
    """
    # This matrix is derived from the XYZ primaries of Rec.2020 and Rec.709.
    # It maps the wide color gamut to the standard gamut.

    # R_709 = 1.6605*R_2020 - 0.5876*G_2020 - 0.0728*B_2020
    # G_709 = -0.1246*R_2020 + 1.1329*G_2020 - 0.0083*B_2020
    # B_709 = -0.0182*R_2020 - 0.1006*G_2020 + 1.1187*B_2020

    # Define the Matrix
    mat = np.array(
        [
            [1.660496, -0.587656, -0.072840],
            [-0.124547, 1.132895, -0.008348],
            [-0.018154, -0.100597, 1.118751],
        ]
    )

    # Apply Matrix
    # We reshape to (N, 3) for dot product then reshape back
    h, w, c = rgb_linear_2020.shape
    flat = rgb_linear_2020.reshape(-1, 3)

    # Dot product: resulting shape (N, 3)
    transformed = np.dot(flat, mat.T)

    rgb_linear_709 = transformed.reshape(h, w, c)

    return rgb_linear_709


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


def write_yuv_plane(av_plane, data_float, width, height):
    """
    Writes float data (0-255 range) into a PyAV plane, handling stride.
    """
    # 1. Convert float data to uint8 (for 8-bit output)
    data_u8 = np.clip(data_float, 0, 255).astype(np.uint8)

    # 2. Get output plane as a numpy view
    # Output format is yuv420p (8-bit), so we use uint8
    stride = av_plane.line_size  # 1 byte per pixel
    out_buffer = np.frombuffer(av_plane, np.uint8)

    # 3. Create a view into the output buffer with correct stride
    out_view = out_buffer[: height * stride].reshape(height, stride)

    # 4. Copy our data into the valid region of the output
    out_view[:, :width] = data_u8


def process_video(input_path, output_path):
    # PyAV allows accessing the raw 10-bit planes, not like OpenCV, which only supports up to 8-bit.
    input_container = av.open(input_path)
    in_stream = input_container.streams.video[0]

    output_container = av.open(output_path, "w")

    out_stream = output_container.add_stream("h264", rate=in_stream.average_rate)
    out_stream.width = in_stream.width
    out_stream.height = in_stream.height
    out_stream.pix_fmt = "yuv420p"

    print(f"Converting PQ -> SDR: {input_path} -> {output_path}...")

    out_stream.options = {
        "crf": "20",
        "preset": "fast",
        "x264-params": "colorprim=bt709:transfer=bt709:colormatrix=bt709",
    }

    for frame in input_container.decode(in_stream):

        # --- 1. Read Input Planes (Fixes AttributeError) ---
        # Luma (Y) - Full Resolution
        y_float = read_yuv_plane(frame.planes[0], frame.width, frame.height)

        # Chroma (U, V) - Half Resolution (4:2:0)
        uv_width = frame.width // 2
        uv_height = frame.height // 2
        u_float = read_yuv_plane(frame.planes[1], uv_width, uv_height)
        v_float = read_yuv_plane(frame.planes[2], uv_width, uv_height)

        # --- 2. Normalize and Resize ---
        # Normalize 10-bit (0-1023) to 0.0-1.0
        y_norm = y_float / 1023.0
        u_norm = u_float / 1023.0
        v_norm = v_float / 1023.0

        # Upscale Chroma to match Y for pixel processing
        u_resized = cv2.resize(
            u_norm, (frame.width, frame.height), interpolation=cv2.INTER_LINEAR
        )
        v_resized = cv2.resize(
            v_norm, (frame.width, frame.height), interpolation=cv2.INTER_LINEAR
        )

        # --- 3. Color Pipeline ---

        # A. YUV -> RGB (Rec.2020)
        rgb_nonlinear = yuv_to_rgb_rec2020(y_norm, u_resized, v_resized)

        # B. Linearize (PQ EOTF) -> Returns Nits
        rgb_linear_nits = eotf_pq10(rgb_nonlinear) * 10000.0

        # C. Scale (npl=100) -> 1.0 = 100 Nits
        rgb_linear_2020 = rgb_linear_nits / 100.0

        # D. Convert Primaries (Rec.2020 -> Rec.709)
        rgb_linear_709 = linear_2020_to_linear_709(rgb_linear_2020)
        rgb_linear_709 = np.maximum(rgb_linear_709, 0.0)  # Clip negatives

        # E. Tone Map (Hable)
        # # **IMPORTANT**: Without this, your video will look blown out.
        # rgb_sdr_linear = hable_tonemap_desat0(rgb_linear_709)

        # F. Apply OETF (Linear -> Gamma Rec.709)
        rgb_gamma_709 = oetf_sdr(rgb_linear_709)

        # G. RGB -> YUV Limited
        y_final, u_final, v_final = rgb_to_yuv420_limited(rgb_gamma_709)

        # --- 4. Write Output Planes (Fixes Stride/Padding issues) ---
        out_frame = av.VideoFrame(
            width=out_stream.width, height=out_stream.height, format="yuv420p"
        )
        out_frame.pts = frame.pts
        out_frame.time_base = frame.time_base

        # Use helper function to write data safely
        write_yuv_plane(
            out_frame.planes[0], y_final, out_stream.width, out_stream.height
        )
        write_yuv_plane(
            out_frame.planes[1], u_final, out_stream.width // 2, out_stream.height // 2
        )
        write_yuv_plane(
            out_frame.planes[2], v_final, out_stream.width // 2, out_stream.height // 2
        )

        for packet in out_stream.encode(out_frame):
            output_container.mux(packet)

    # Flush the encoder (write buffered frames)
    for packet in out_stream.encode():
        output_container.mux(packet)

    # Close files
    input_container.close()
    output_container.close()
    print("Done!")


# Usage
output_dir = "./output"
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "test_pq2sdr.mp4")
process_video(INPUT_VIDEO, output_path)
