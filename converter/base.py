import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

import av
import numpy as np

from utils import (
    read_plane_8bit,
    read_plane_10bit,
    write_plane_8bit,
    write_plane_10bit,
)


class Transfer(Enum):
    SDR = "bt709"
    PQ = "smpte2084"
    HLG = "arib-std-b67"


class Primaries(Enum):
    BT709 = "bt709"
    BT2020 = "bt2020"


@dataclass(frozen=True)
class Format:
    primaries: Primaries
    transfer: Transfer
    bit_depth: int

    @property
    def pix_fmt(self) -> str:
        return "yuv420p10le" if self.bit_depth == 10 else "yuv420p"


# Predefined formats
SDR = Format(Primaries.BT709, Transfer.SDR, 8)
PQ = Format(Primaries.BT2020, Transfer.PQ, 10)
HLG = Format(Primaries.BT2020, Transfer.HLG, 10)


class VideoConverter(ABC):
    """Base class for video conversions."""

    def __init__(self, input_path: str, output_path: str = None):
        self.input_path = input_path
        if output_path is None:
            base, ext = os.path.splitext(input_path)
            output_dir = "../output"
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(
                output_dir,
                f"test_{self.__class__.__name__.lower()}{ext}",
            )

        self.output_path = output_path

    @property
    @abstractmethod
    def src_format(self) -> Format:
        raise NotImplementedError

    @property
    @abstractmethod
    def dst_format(self) -> Format:
        raise NotImplementedError

    @abstractmethod
    def decode_to_linear(self, y, u, v, w, h) -> np.ndarray:
        """Decode YUV to linear RGB."""
        raise NotImplementedError

    @abstractmethod
    def encode_from_linear(self, rgb_linear) -> tuple:
        """Encode linear RGB to YUV (y, u, v)."""
        raise NotImplementedError

    def _get_encoder_options(self) -> dict:
        fmt = self.dst_format
        if fmt.bit_depth == 10:
            t = fmt.transfer.value
            return {
                "crf": "20",
                "preset": "fast",
                "x265-params": f"colorprim=bt2020:transfer={t}:colormatrix=bt2020nc",
            }
        return {
            "crf": "20",
            "preset": "fast",
            "x264-params": "colorprim=bt709:transfer=bt709:colormatrix=bt709",
        }

    def process(self):
        # PyAV allows accessing the raw 10-bit planes, not like OpenCV, which only supports up to 8-bit.
        input_container = av.open(self.input_path)
        input_stream = input_container.streams.video[0]

        output_container = av.open(self.output_path, "w")
        codec = "hevc" if self.dst_format.bit_depth == 10 else "h264"
        output_stream = output_container.add_stream(
            codec, rate=input_stream.average_rate
        )
        output_stream.width = input_stream.width
        output_stream.height = input_stream.height
        output_stream.pix_fmt = self.dst_format.pix_fmt

        if self.dst_format.bit_depth == 10:
            output_stream.codec_context.codec_tag = "hvc1"
        output_stream.options = self._get_encoder_options()

        print(f"Converting: {self.input_path} -> {self.output_path}")

        for frame in input_container.decode(input_stream):
            w, h = frame.width, frame.height
            uv_w, uv_h = w // 2, h // 2

            # Read
            if self.src_format.bit_depth == 10:
                y = read_plane_10bit(frame.planes[0], w, h)
                u = read_plane_10bit(frame.planes[1], uv_w, uv_h)
                v = read_plane_10bit(frame.planes[2], uv_w, uv_h)
            else:
                y = read_plane_8bit(frame.planes[0], w, h)
                u = read_plane_8bit(frame.planes[1], uv_w, uv_h)
                v = read_plane_8bit(frame.planes[2], uv_w, uv_h)

            # Convert
            rgb_linear = self.decode_to_linear(y, u, v, w, h)
            y_out, u_out, v_out = self.encode_from_linear(rgb_linear)

            # Write
            out_frame = av.VideoFrame(width=w, height=h, format=self.dst_format.pix_fmt)
            out_frame.pts = frame.pts
            out_frame.time_base = frame.time_base

            if self.dst_format.bit_depth == 10:
                write_plane_10bit(out_frame.planes[0], y_out, w, h)
                write_plane_10bit(out_frame.planes[1], u_out, uv_w, uv_h)
                write_plane_10bit(out_frame.planes[2], v_out, uv_w, uv_h)
            else:
                write_plane_8bit(out_frame.planes[0], y_out, w, h)
                write_plane_8bit(out_frame.planes[1], u_out, uv_w, uv_h)
                write_plane_8bit(out_frame.planes[2], v_out, uv_w, uv_h)

            for pkt in output_stream.encode(out_frame):
                output_container.mux(pkt)

        for pkt in output_stream.encode():
            output_container.mux(pkt)

        input_container.close()
        output_container.close()
        print("Done!")
