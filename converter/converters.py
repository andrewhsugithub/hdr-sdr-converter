import numpy as np

from utils import (
    downsample_chroma,
    eotf_hlg,
    eotf_pq,
    eotf_sdr,
    linear_709_to_2020,
    linear_2020_to_709,
    normalize_8bit,
    normalize_10bit,
    oetf_hlg,
    oetf_pq,
    oetf_sdr,
    quantize_8bit,
    quantize_10bit,
    rgb_to_yuv_709,
    rgb_to_yuv_2020,
    upsample_chroma,
    yuv_to_rgb_709,
    yuv_to_rgb_2020,
)

from .base import HLG, PQ, SDR, Format, Primaries, VideoConverter


class SDR2PQ(VideoConverter):
    def __init__(self, input_path, output_path=None):
        super().__init__(input_path, output_path)

    @property
    def src_format(self) -> Format:
        return SDR

    @property
    def dst_format(self) -> Format:
        return PQ

    def decode_to_linear(self, y, u, v, w, h):
        y_norm, u_norm, v_norm = normalize_8bit(y, u, v)
        u_up, v_up = upsample_chroma(u_norm, v_norm, w, h)
        rgb = yuv_to_rgb_709(y_norm, u_up, v_up)
        rgb_linear = eotf_sdr(rgb)
        rgb_2020 = linear_709_to_2020(rgb_linear)
        return np.clip(rgb_2020, 0, None)

    def encode_from_linear(self, rgb_linear):
        # map sdr to pq
        # 203 nits is recommended in BT.2408-8
        rgb_scaled = rgb_linear * (203.0 / 10000.0)
        rgb_scaled = np.clip(rgb_scaled, 0, 1)
        rgb_pq = oetf_pq(rgb_scaled)
        y, u, v = rgb_to_yuv_2020(rgb_pq)
        u_down, v_down = downsample_chroma(u, v)
        return quantize_10bit(y, u_down, v_down)


class SDR2HLG(VideoConverter):
    def __init__(self, input_path, output_path=None):
        super().__init__(input_path, output_path)

    @property
    def src_format(self) -> Format:
        return SDR

    @property
    def dst_format(self) -> Format:
        return HLG

    def decode_to_linear(self, y, u, v, w, h):
        y_norm, u_norm, v_norm = normalize_8bit(y, u, v)
        u_up, v_up = upsample_chroma(u_norm, v_norm, w, h)
        rgb = yuv_to_rgb_709(y_norm, u_up, v_up)
        rgb_linear = eotf_sdr(rgb)
        rgb_2020 = linear_709_to_2020(rgb_linear)
        return np.clip(rgb_2020, 0, None)

    def encode_from_linear(self, rgb_linear):
        # map sdr to hlg
        # 203 nits is recommended in BT.2408-8
        rgb_scaled = rgb_linear * (203.0 / 1000.0)
        rgb_scaled = np.clip(rgb_scaled, 0, 1)
        rgb_hlg = oetf_hlg(rgb_scaled)
        y, u, v = rgb_to_yuv_2020(rgb_hlg)
        u_down, v_down = downsample_chroma(u, v)
        return quantize_10bit(y, u_down, v_down)


class PQ2SDR(VideoConverter):
    def __init__(self, input_path, output_path=None):
        super().__init__(input_path, output_path)

    @property
    def src_format(self) -> Format:
        return PQ

    @property
    def dst_format(self) -> Format:
        return SDR

    def decode_to_linear(self, y, u, v, w, h):
        y_norm, u_norm, v_norm = normalize_10bit(y, u, v)
        u_up, v_up = upsample_chroma(u_norm, v_norm, w, h)
        rgb = yuv_to_rgb_2020(y_norm, u_up, v_up)
        rgb_linear = eotf_pq(np.clip(rgb, 0, 1))
        return np.clip(rgb_linear, 0, None)

    def encode_from_linear(self, rgb_linear):
        # map pq to sdr
        rgb_scaled = rgb_linear * (10000.0 / 100.0)
        rgb_scaled = np.clip(rgb_scaled, 0, 1)
        rgb_709 = linear_2020_to_709(rgb_scaled)
        rgb_709 = np.clip(rgb_709, 0, 1)
        rgb_sdr = oetf_sdr(rgb_709)
        y, u, v = rgb_to_yuv_709(rgb_sdr)
        u_down, v_down = downsample_chroma(u, v)
        return quantize_8bit(y, u_down, v_down)


class HLG2SDR(VideoConverter):
    def __init__(self, input_path, output_path=None):
        super().__init__(input_path, output_path)

    @property
    def src_format(self) -> Format:
        return HLG

    @property
    def dst_format(self) -> Format:
        return SDR

    def decode_to_linear(self, y, u, v, w, h):
        y_norm, u_norm, v_norm = normalize_10bit(y, u, v)
        u_up, v_up = upsample_chroma(u_norm, v_norm, w, h)
        rgb = yuv_to_rgb_2020(y_norm, u_up, v_up)
        rgb_linear = eotf_hlg(np.clip(rgb, 0, 1))
        return np.clip(rgb_linear, 0, None)

    def encode_from_linear(self, rgb_linear):
        # convert scene light to display light (HLG OOTF)
        rgb_linear = np.power(rgb_linear, 1.2)
        # map hlg to sdr
        rgb_scaled = rgb_linear * (1000.0 / 100.0)
        rgb_scaled = np.clip(rgb_scaled, 0, 1)
        rgb_709 = linear_2020_to_709(rgb_scaled)
        rgb_709 = np.clip(rgb_709, 0, 1)
        rgb_sdr = oetf_sdr(rgb_709)
        y, u, v = rgb_to_yuv_709(rgb_sdr)
        u_down, v_down = downsample_chroma(u, v)
        return quantize_8bit(y, u_down, v_down)


class PQ2HLG(VideoConverter):
    def __init__(self, input_path, output_path=None):
        super().__init__(input_path, output_path)

    @property
    def src_format(self) -> Format:
        return PQ

    @property
    def dst_format(self) -> Format:
        return HLG

    def decode_to_linear(self, y, u, v, w, h):
        y_norm, u_norm, v_norm = normalize_10bit(y, u, v)
        u_up, v_up = upsample_chroma(u_norm, v_norm, w, h)
        rgb = yuv_to_rgb_2020(y_norm, u_up, v_up)
        rgb_linear = eotf_pq(np.clip(rgb, 0, 1))
        return np.clip(rgb_linear, 0, None)

    def encode_from_linear(self, rgb_linear):
        # map pq to hlg
        rgb_scaled = rgb_linear * (10000.0 / 1000.0)
        rgb_scaled = np.clip(rgb_scaled, 0, 1)
        # convert display light to scene light
        rgb_scene = np.power(rgb_scaled, 1 / 1.2)
        rgb_hlg = oetf_hlg(rgb_scene)
        y, u, v = rgb_to_yuv_2020(rgb_hlg)
        u_down, v_down = downsample_chroma(u, v)
        return quantize_10bit(y, u_down, v_down)


class HLG2PQ(VideoConverter):
    def __init__(self, input_path, output_path=None):
        super().__init__(input_path, output_path)

    @property
    def src_format(self) -> Format:
        return HLG

    @property
    def dst_format(self) -> Format:
        return PQ

    def decode_to_linear(self, y, u, v, w, h):
        y_norm, u_norm, v_norm = normalize_10bit(y, u, v)
        u_up, v_up = upsample_chroma(u_norm, v_norm, w, h)
        rgb = yuv_to_rgb_2020(y_norm, u_up, v_up)
        rgb_linear = eotf_hlg(np.clip(rgb, 0, 1))
        return np.clip(rgb_linear, 0, None)

    def encode_from_linear(self, rgb_linear):
        # convert scene light to display light
        rgb_linear = np.power(rgb_linear, 1.2)
        # map hlg to pq
        rgb_scaled = rgb_linear * (1000.0 / 10000.0)
        rgb_scaled = np.clip(rgb_scaled, 0, 1)
        rgb_pq = oetf_pq(rgb_scaled)
        y, u, v = rgb_to_yuv_2020(rgb_pq)
        u_down, v_down = downsample_chroma(u, v)
        return quantize_10bit(y, u_down, v_down)


class Rewrap(VideoConverter):
    """Copy pixels without transfer functions (for comparison)."""

    def __init__(self, input_path, output_path=None, src_fmt=PQ, dst_fmt=HLG):
        super().__init__(input_path, output_path)
        self._src_fmt = src_fmt
        self._dst_fmt = dst_fmt

    @property
    def src_format(self) -> Format:
        return self._src_fmt

    @property
    def dst_format(self) -> Format:
        return self._dst_fmt

    def decode_to_linear(self, y, u, v, w, h):
        if self._src_fmt.bit_depth == 10:
            y_norm, u_norm, v_norm = normalize_10bit(y, u, v)
        else:
            y_norm, u_norm, v_norm = normalize_8bit(y, u, v)
        u_up, v_up = upsample_chroma(u_norm, v_norm, w, h)
        if self._src_fmt.primaries == Primaries.BT2020:
            rgb = yuv_to_rgb_2020(y_norm, u_up, v_up)
        else:
            rgb = yuv_to_rgb_709(y_norm, u_up, v_up)
        if (
            self._src_fmt.primaries == Primaries.BT709
            and self._dst_fmt.primaries == Primaries.BT2020
        ):
            rgb = linear_709_to_2020(rgb)
        # Skip EOTF
        return np.clip(rgb, 0, 1)

    def encode_from_linear(self, rgb):
        # Skip OETF
        rgb = np.clip(rgb, 0, 1)
        if (
            self._src_fmt.primaries == Primaries.BT2020
            and self._dst_fmt.primaries == Primaries.BT709
        ):
            rgb = linear_2020_to_709(rgb)
            rgb = np.clip(rgb, 0, 1)
        if self._dst_fmt.primaries == Primaries.BT2020:
            y, u, v = rgb_to_yuv_2020(rgb)
        else:
            y, u, v = rgb_to_yuv_709(rgb)
        u_down, v_down = downsample_chroma(u, v)
        if self._dst_fmt.bit_depth == 10:
            return quantize_10bit(y, u_down, v_down)
        else:
            return quantize_8bit(y, u_down, v_down)
