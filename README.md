# HDR ↔️ SDR Video Converter

A lightweight command-line toolkit for converting video between SDR (Rec.709) and HDR formats (Rec.2100 HLG or PQ). It handles color-space transforms, tone-mapping, transfer functions, and bit-depth conversions with precision. The tool also lets you compare FFmpeg-based and Python-based conversion pipelines, generate test outputs for validation, and create rewrapped files that modify metadata without using transfer functions.

## Setup

> See .python-version for python version used.

1. Create a virtual environment:

   ```bash
   python -m venv .venv
   ```

   or if using [uv](https://docs.astral.sh/uv/getting-started/installation/):

   ```bash
   uv venv
   ```

2. Activate the virtual environment:

   ```bash
   source .venv/bin/activate
   ```

3. Install dependencies from `pyproject.toml`:

   ```bash
   pip install .
   ```

   or if using [uv](https://docs.astral.sh/uv/getting-started/installation/):

   ```bash
   uv sync
   # or
   uv pip install -r pyproject.toml
   ```

## Usage

CLI

- Run converter:
  ```bash
  python main.py <command> -i <path/to/input.mp4> [-o <path/to/output.mp4>]
  # or uv
  uv run main.py <command> -i <path/to/input.mp4> [-o <path/to/output.mp4>]
  ```
- List available conversions:
  ```bash
  python main.py list
  # or uv
  uv run main.py list
  ```

Commands

- sdr2pq, sdr2hlg, pq2sdr, hlg2sdr, pq2hlg, hlg2pq - convert between formats
- rewrap — copy pixels and change metadata (use --src and --dst to specify formats)

Formats

- sdr — BT.709, 8-bit
- pq — BT.2100 PQ (HDR10), 10-bit
- hlg — BT.2100 HLG, 10-bit

Default output paths (when -o omitted)

- For conversion commands: `output/test_<command>.mp4`
- For rewrap: `output/rewrap/test<src>2<dst>rewrapped.mp4`

Examples

- List commands:
  ```bash
  python main.py list
  # or uv
  uv run main.py list
  ```
- Convert SDR → HLG:
  ```bash
  python main.py sdr2hlg -i test_sdr.mp4
  # or uv
  uv run main.py sdr2hlg -i test_sdr.mp4
  ```
- Convert PQ → SDR and write to custom file:
  ```bash
  python main.py pq2sdr -i test_pq.mp4 -o ./output/ffmpeg/pq2sdr.mp4
  # or uv
  uv run main.py pq2sdr -i test_pq.mp4 -o ./output/ffmpeg/pq2sdr.mp4
  ```
- Rewrap (change metadata):
  ```bash
  python main.py rewrap -i test_sdr.mp4 --src sdr --dst hlg
  # or uv
  uv run main.py rewrap -i test_sdr.mp4 --src sdr --dst hlg
  ```

Notes:

- Use -o to control the output path; parent directories will be created automatically.
- If you rely on ffmpeg in examples, ensure ffmpeg is installed and on PATH.
- For reproducible results, keep source/target format metadata consistent with the files you provide.

## Test Video Used (test\_\*.mp4)

### HDR PQ Test Video

[![HDR PQ Test Video](https://img.youtube.com/vi/tSEKX2mx0q0/0.jpg)](https://youtu.be/tSEKX2mx0q0)

1. Download at https://www.demolandia.net/downloads.html?id=654828652

2. Save as `demo_pq.mp4` in the project root directory.

3. Downscale to 1920x1080 and trim the 32-39 seconds segment for testing:

```bash
# need to install ffmpeg first
ffmpeg -i demo_pq.mp4 -vf "fps=30,scale=1920:1080" -ss 32 -to 39 -c:v libx265 -crf 23 -preset fast -tag:v hvc1 -an test_pq.mp4
```

  <video src="test_pq.mp4" placeholder="Test HDR PQ Video" autoplay loop controls muted title="Test HDR PQ Video">
  Test HDR PQ Video</video>

https://github.com/user-attachments/assets/2ad463fe-e470-440e-8216-cc9b7902c4e5

<details>
  <summary style="font-weight: bold; font-size: 24px">Check PQ Test Video Details</summary>

- Video Details from Apple QuickTimePlayer's Video Inspector (_Command + I_):

  | Property          | Value              |
  | ----------------- | ------------------ |
  | Bit Depth         | 10-bit             |
  | HDR Type          | HDR10              |
  | Color Primaries   | ITU-R BT.2020      |
  | Transfer Function | SMPTE ST 2084 (PQ) |
  | YCbCr Matrix      | ITU-R BT.2020      |

- or determine the video properties using `ffprobe`:

  ```bash
  ffprobe -v quiet -show_streams -select_streams v:0 -of json test_pq.mp4
  ```

- Output:

  ```json
  {
    "streams": [
      {
        "index": 0,
        "codec_name": "hevc",
        "codec_long_name": "H.265 / HEVC (High Efficiency Video Coding)",
        "profile": "Main 10",
        "codec_type": "video",
        "codec_tag_string": "hvc1",
        "codec_tag": "0x31637668",
        "width": 1920,
        "height": 1080,
        "coded_width": 1920,
        "coded_height": 1080,
        "has_b_frames": 2,
        "sample_aspect_ratio": "1:1",
        "display_aspect_ratio": "16:9",
        "pix_fmt": "yuv420p10le",
        "level": 120,
        "color_range": "tv",
        "color_space": "bt2020nc",
        "color_transfer": "smpte2084",
        "color_primaries": "bt2020",
        "chroma_location": "left",
        "field_order": "progressive",
        "refs": 1,
        "view_ids_available": "",
        "view_pos_available": "",
        "id": "0x1",
        "r_frame_rate": "30/1",
        "avg_frame_rate": "30/1",
        "time_base": "1/15360",
        "start_pts": 0,
        "start_time": "0.000000",
        "duration_ts": 107520,
        "duration": "7.000000",
        "bit_rate": "9459573",
        "nb_frames": "210",
        "extradata_size": 2556,
        "disposition": {
          "default": 1,
          "dub": 0,
          "original": 0,
          "comment": 0,
          "lyrics": 0,
          "karaoke": 0,
          "forced": 0,
          "hearing_impaired": 0,
          "visual_impaired": 0,
          "clean_effects": 0,
          "attached_pic": 0,
          "timed_thumbnails": 0,
          "non_diegetic": 0,
          "captions": 0,
          "descriptions": 0,
          "metadata": 0,
          "dependent": 0,
          "still_image": 0,
          "multilayer": 0
        },
        "tags": {
          "language": "und",
          "handler_name": "Video Media Handler",
          "vendor_id": "[0][0][0][0]",
          "encoder": "Lavc62.11.100 libx265"
        },
        "side_data_list": [
          {
            "side_data_type": "Content light level metadata",
            "max_content": 0,
            "max_average": 0
          }
        ]
      }
    ]
  }
  ```

  From the above, we can see that the video is encoded in HDR (10-bit YUV 4:2:0) and uses PQ10 as the transfer function.
  </details>

### HDR HLG Test Video

[![HDR HLG Test Video](https://img.youtube.com/vi/3ypGuk6JC6M/0.jpg)](https://youtu.be/3ypGuk6JC6M)

1. Save as `demo_hlg.mp4` in the project root directory.

2. Trim the 29-32 seconds segment for testing:

```bash
# need to install ffmpeg first
ffmpeg -i test_hlg.mp4 -ss 29 -to 32 -c:v libx265 -crf 23 -preset fast -tag:v hvc1 test_hlg.mp4
```

<video src="test_hlg.mp4" placeholder="Test HDR HLG Video" autoplay loop controls muted title="Test HDR HLG Video">
Test HDR HLG Video</video>

https://github.com/user-attachments/assets/3630df24-6a10-4fc7-9649-e35f7980f555

<details>
  <summary style="font-weight: bold; font-size: 24px">Check HLG Test Video Details</summary>

- Video Details from Apple QuickTimePlayer's Video Inspector (_Command + I_):

  | Property          | Value               |
  | ----------------- | ------------------- |
  | Bit Depth         | 10-bit              |
  | HDR Type          | HLG                 |
  | Color Primaries   | ITU-R BT.2020       |
  | Transfer Function | SMPTE ST 2100 (HLG) |
  | YCbCr Matrix      | ITU-R BT.2020       |

- or determine the video properties using `ffprobe`:

  ```bash
  ffprobe -v quiet -show_streams -select_streams v:0 -of json test_hlg.mp4
  ```

- Output:

  ```json
  {
    "streams": [
      {
        "index": 0,
        "codec_name": "hevc",
        "codec_long_name": "H.265 / HEVC (High Efficiency Video Coding)",
        "profile": "Main 10",
        "codec_type": "video",
        "codec_tag_string": "hvc1",
        "codec_tag": "0x31637668",
        "width": 1920,
        "height": 1080,
        "coded_width": 1920,
        "coded_height": 1080,
        "has_b_frames": 2,
        "sample_aspect_ratio": "1:1",
        "display_aspect_ratio": "16:9",
        "pix_fmt": "yuv420p10le",
        "level": 120,
        "color_range": "tv",
        "color_space": "bt2020nc",
        "color_transfer": "arib-std-b67",
        "color_primaries": "bt2020",
        "chroma_location": "left",
        "field_order": "progressive",
        "refs": 1,
        "view_ids_available": "",
        "view_pos_available": "",
        "id": "0x1",
        "r_frame_rate": "30000/1001",
        "avg_frame_rate": "30000/1001",
        "time_base": "1/30000",
        "start_pts": 990,
        "start_time": "0.033000",
        "duration_ts": 89089,
        "duration": "2.969633",
        "bit_rate": "2642966",
        "nb_frames": "89",
        "extradata_size": 2595,
        "disposition": {
          "default": 1,
          "dub": 0,
          "original": 0,
          "comment": 0,
          "lyrics": 0,
          "karaoke": 0,
          "forced": 0,
          "hearing_impaired": 0,
          "visual_impaired": 0,
          "clean_effects": 0,
          "attached_pic": 0,
          "timed_thumbnails": 0,
          "non_diegetic": 0,
          "captions": 0,
          "descriptions": 0,
          "metadata": 0,
          "dependent": 0,
          "still_image": 0,
          "multilayer": 0
        },
        "tags": {
          "language": "eng",
          "handler_name": "VideoHandler",
          "vendor_id": "[0][0][0][0]",
          "encoder": "Lavc62.11.100 libx265"
        },
        "side_data_list": [
          {
            "side_data_type": "Mastering display metadata",
            "red_x": "34000/50000",
            "red_y": "16000/50000",
            "green_x": "13248/50000",
            "green_y": "34500/50000",
            "blue_x": "7500/50000",
            "blue_y": "3000/50000",
            "white_point_x": "15634/50000",
            "white_point_y": "16450/50000",
            "min_luminance": "50/10000",
            "max_luminance": "10000000/10000"
          },
          {
            "side_data_type": "Content light level metadata",
            "max_content": 0,
            "max_average": 0
          }
        ]
      }
    ]
  }
  ```

  From the above, we can see that the video is encoded in HDR (10-bit YUV 4:2:0) and uses HLG as the transfer function.
  </details>

### SDR Test Video

<video src="test_sdr.mp4" placeholder="Test SDR Video" autoplay loop controls muted title="Test SDR Video"></video>

https://github.com/user-attachments/assets/44cc7874-e29a-4ccb-b1c3-ee3a3f375e98

1. Download Big Buck Bunny from https://test-videos.co.uk/vids/bigbuckbunny/mp4/h264/1080/Big_Buck_Bunny_1080_10s_1MB.mp4

2. Save as `test_sdr.mp4` in the project root directory.

<details>
  <summary style="font-weight: bold; font-size: 24px">Check HLG Test Video Details</summary>

- Determine the video properties using `ffprobe`:

  ```bash
  ffprobe -v quiet -show_streams -select_streams v:0 -of json test_sdr.mp4
  ```

- Output:

  ```json
  {
    "streams": [
      {
        "index": 0,
        "codec_name": "h264",
        "codec_long_name": "H.264 / AVC / MPEG-4 AVC / MPEG-4 part 10",
        "profile": "High",
        "codec_type": "video",
        "codec_tag_string": "avc1",
        "codec_tag": "0x31637661",
        "width": 1920,
        "height": 1080,
        "coded_width": 1920,
        "coded_height": 1080,
        "has_b_frames": 2,
        "sample_aspect_ratio": "1:1",
        "display_aspect_ratio": "16:9",
        "pix_fmt": "yuv420p",
        "level": 51,
        "chroma_location": "left",
        "field_order": "progressive",
        "refs": 1,
        "is_avc": "true",
        "nal_length_size": "4",
        "id": "0x1",
        "r_frame_rate": "30/1",
        "avg_frame_rate": "30/1",
        "time_base": "1/15360",
        "start_pts": 0,
        "start_time": "0.000000",
        "duration_ts": 153600,
        "duration": "10.000000",
        "bit_rate": "24559867",
        "bits_per_raw_sample": "8",
        "nb_frames": "300",
        "extradata_size": 47,
        "disposition": {
          "default": 1,
          "dub": 0,
          "original": 0,
          "comment": 0,
          "lyrics": 0,
          "karaoke": 0,
          "forced": 0,
          "hearing_impaired": 0,
          "visual_impaired": 0,
          "clean_effects": 0,
          "attached_pic": 0,
          "timed_thumbnails": 0,
          "non_diegetic": 0,
          "captions": 0,
          "descriptions": 0,
          "metadata": 0,
          "dependent": 0,
          "still_image": 0,
          "multilayer": 0
        },
        "tags": {
          "language": "und",
          "handler_name": "VideoHandler",
          "vendor_id": "[0][0][0][0]"
        }
      }
    ]
  }
  ```

  From the above, we can see that the video is encoded in SDR (8-bit YUV 4:2:0).
  </details>

## Results

The converted videos are saved in the `output/` directory:

1. HDR (PQ10) ➡️ SDR Conversion

- `output/ffmpeg/pq2sdr.mp4`: Converted to SDR using ffmpeg command:

  ```bash
  ffmpeg -i test_pq.mp4 -vf "zscale=t=linear:npl=100, format=gbrpf32le, zscale=p=bt709, zscale=t=bt709:m=bt709:r=tv, format=yuv420p" ./output/ffmpeg/pq2sdr.mp4
  ```

  <details>
    <summary>Video Details from Apple QuickTimePlayer's Video Inspector <span style="font-style: italic;">(Command + I)</span>:</summary>
    
    | Property          | Value               |
    | ----------------- | ------------------- |
    | Color Primaries   | ITU-R BT.709        |
    | Transfer Function | ITU-R BT.709        |
    | YCbCr Matrix      | ITU-R BT.709        |

  </details>

- `output/test_pq2sdr.mp4`: Converted using `main.py` command:

  ```bash
  python main.py pq2sdr -i test_pq.mp4
  # or using uv
  uv run main.py pq2sdr -i test_pq.mp4
  ```

  <details>
    <summary>Video Details using <span style="font-style: italic;">ffprobe</span> (same as above command just diff file):</summary>

  ```json
  {
    "streams": [
      {
        "index": 0,
        "codec_name": "h264",
        "codec_long_name": "H.264 / AVC / MPEG-4 AVC / MPEG-4 part 10",
        "profile": "High",
        "codec_type": "video",
        "codec_tag_string": "avc1",
        "codec_tag": "0x31637661",
        "width": 1920,
        "height": 1080,
        "coded_width": 1920,
        "coded_height": 1080,
        "has_b_frames": 2,
        "pix_fmt": "yuv420p",
        "level": 40,
        "color_range": "tv",
        "color_space": "bt709",
        "color_transfer": "bt709",
        "color_primaries": "bt709",
        "chroma_location": "left",
        "field_order": "progressive",
        "refs": 1,
        "is_avc": "true",
        "nal_length_size": "4",
        "id": "0x1",
        "r_frame_rate": "30/1",
        "avg_frame_rate": "30/1",
        "time_base": "1/15360",
        "start_pts": 0,
        "start_time": "0.000000",
        "duration_ts": 107520,
        "duration": "7.000000",
        "bit_rate": "24181306",
        "bits_per_raw_sample": "8",
        "nb_frames": "210",
        "extradata_size": 50,
        "disposition": {
          "default": 1,
          "dub": 0,
          "original": 0,
          "comment": 0,
          "lyrics": 0,
          "karaoke": 0,
          "forced": 0,
          "hearing_impaired": 0,
          "visual_impaired": 0,
          "clean_effects": 0,
          "attached_pic": 0,
          "timed_thumbnails": 0,
          "non_diegetic": 0,
          "captions": 0,
          "descriptions": 0,
          "metadata": 0,
          "dependent": 0,
          "still_image": 0,
          "multilayer": 0
        },
        "tags": {
          "language": "und",
          "handler_name": "VideoHandler",
          "vendor_id": "[0][0][0][0]"
        }
      }
    ]
  }
  ```

  </details>

- `output/rewrap/test_pq2sdr_rewrapped.mp4`: Rewrap (convert without using transfer functions, changed metadata) using `main.py` command:

  ```bash
  python main.py rewrap -i test_pq.mp4 --src pq --dst sdr
  # or using uv
  uv run main.py rewrap -i test_pq.mp4 --src pq --dst sdr
  ```

  <details>
    <summary>Video Details using <span style="font-style: italic;">ffprobe</span> (same as above command just diff file):</summary>

  ```json
  {
    "streams": [
      {
        "index": 0,
        "codec_name": "h264",
        "codec_long_name": "H.264 / AVC / MPEG-4 AVC / MPEG-4 part 10",
        "profile": "High",
        "codec_type": "video",
        "codec_tag_string": "avc1",
        "codec_tag": "0x31637661",
        "width": 1920,
        "height": 1080,
        "coded_width": 1920,
        "coded_height": 1080,
        "has_b_frames": 2,
        "pix_fmt": "yuv420p",
        "level": 40,
        "color_range": "tv",
        "color_space": "bt709",
        "color_transfer": "bt709",
        "color_primaries": "bt709",
        "chroma_location": "left",
        "field_order": "progressive",
        "refs": 1,
        "is_avc": "true",
        "nal_length_size": "4",
        "id": "0x1",
        "r_frame_rate": "30/1",
        "avg_frame_rate": "30/1",
        "time_base": "1/15360",
        "start_pts": 0,
        "start_time": "0.000000",
        "duration_ts": 107520,
        "duration": "7.000000",
        "bit_rate": "15408329",
        "bits_per_raw_sample": "8",
        "nb_frames": "210",
        "extradata_size": 50,
        "disposition": {
          "default": 1,
          "dub": 0,
          "original": 0,
          "comment": 0,
          "lyrics": 0,
          "karaoke": 0,
          "forced": 0,
          "hearing_impaired": 0,
          "visual_impaired": 0,
          "clean_effects": 0,
          "attached_pic": 0,
          "timed_thumbnails": 0,
          "non_diegetic": 0,
          "captions": 0,
          "descriptions": 0,
          "metadata": 0,
          "dependent": 0,
          "still_image": 0,
          "multilayer": 0
        },
        "tags": {
          "language": "und",
          "handler_name": "VideoHandler",
          "vendor_id": "[0][0][0][0]"
        }
      }
    ]
  }
  ```

  </details>

- Comparison
  | Original HDR PQ | Converted SDR using ffmpeg | Converted SDR using main.py | Rewrapped SDR using main.py |
  |---|---|---|---|
  |<video src="https://github.com/user-attachments/assets/2ad463fe-e470-440e-8216-cc9b7902c4e5" placeholder="Test HDR PQ Video" autoplay loop controls muted title="Test HDR PQ Video"></video>|<video src="https://github.com/user-attachments/assets/e0472e23-deaf-416f-8404-dc488b058d2a" placeholder="Converted SDR using ffmpeg" autoplay loop controls muted title="Converted SDR using ffmpeg"></video>|<video src="https://github.com/user-attachments/assets/f5e7df55-9019-4963-a37c-0301379b3559" placeholder="Converted SDR using main.py" autoplay loop controls muted title="Converted SDR using main.py"></video>|<video src="https://github.com/user-attachments/assets/f12babf6-ff98-4208-9892-6c0789ec48a0" placeholder="Rewrapped SDR using main.py" autoplay loop controls muted title="Rewrapped SDR using main.py"></video>|

2. HDR (PQ10) ➡️ HDR (HLG) Conversion

- `output/ffmpeg/pq2hlg.mp4`: Converted to HLG using ffmpeg command:

  ```bash
  ffmpeg -i test.mp4 -vf "zscale=t=arib-std-b67" -c:v libx265 -crf 20 -preset fast -tag:v hvc1 ./output/ffmpeg/pq2hlg.mp4
  ```

  <details>
   <summary>Video Details from Apple QuickTimePlayer's Video Inspector <span style="font-style: italic;">(Command + I)</span>:</summary>

  | Property          | Value               |
  | ----------------- | ------------------- |
  | Bit Depth         | 10-bit              |
  | HDR Type          | HLG                 |
  | Color Primaries   | ITU-R BT.2020       |
  | Transfer Function | SMPTE ST 2100 (HLG) |
  | YCbCr Matrix      | ITU-R BT.2020       |

  </details>

- `output/test_pq2hlg.mp4`: Converted using `main.py` command:

  ```bash
  python main.py pq2hlg -i test_pq.mp4
  # or using uv
  uv run main.py pq2hlg -i test_pq.mp4
  ```

  <details>
    <summary>Video Details using <span style="font-style: italic;">ffprobe</span> (same as above command just diff file):</summary>
    
    ```json
    {
      "streams": [
        {
          "index": 0,
          "codec_name": "hevc",
          "codec_long_name": "H.265 / HEVC (High Efficiency Video Coding)",
          "profile": "Main 10",
          "codec_type": "video",
          "codec_tag_string": "hvc1",
          "codec_tag": "0x31637668",
          "width": 1920,
          "height": 1080,
          "coded_width": 1920,
          "coded_height": 1080,
          "has_b_frames": 2,
          "pix_fmt": "yuv420p10le",
          "level": 120,
          "color_range": "tv",
          "color_space": "bt2020nc",
          "color_transfer": "arib-std-b67",
          "color_primaries": "bt2020",
          "chroma_location": "left",
          "refs": 1,
          "view_ids_available": "",
          "view_pos_available": "",
          "id": "0x1",
          "r_frame_rate": "30/1",
          "avg_frame_rate": "30/1",
          "time_base": "1/15360",
          "start_pts": 0,
          "start_time": "0.000000",
          "duration_ts": 107520,
          "duration": "7.000000",
          "bit_rate": "12564515",
          "nb_frames": "210",
          "extradata_size": 2438,
          "disposition": {
            "default": 1,
            "dub": 0,
            "original": 0,
            "comment": 0,
            "lyrics": 0,
            "karaoke": 0,
            "forced": 0,
            "hearing_impaired": 0,
            "visual_impaired": 0,
            "clean_effects": 0,
            "attached_pic": 0,
            "timed_thumbnails": 0,
            "non_diegetic": 0,
            "captions": 0,
            "descriptions": 0,
            "metadata": 0,
            "dependent": 0,
            "still_image": 0,
            "multilayer": 0
          },
          "tags": {
            "language": "und",
            "handler_name": "VideoHandler",
            "vendor_id": "[0][0][0][0]"
          }
        }
      ]
    }
    ```
  </details>

- `output/rewrap/test_pq2hlg_rewrapped.mp4`: Rewrap (convert without using transfer functions, changed metadata) using `main.py` command:

  ```bash
  python main.py rewrap -i test_pq.mp4 --src pq --dst hlg
  # or using uv
  uv run main.py rewrap -i test_pq.mp4 --src pq --dst hlg
  ```

  <details>
    <summary>Video Details using <span style="font-style: italic;">ffprobe</span> (same as above command just diff file):</summary>

  ```json
  {
    "streams": [
      {
        "index": 0,
        "codec_name": "hevc",
        "codec_long_name": "H.265 / HEVC (High Efficiency Video Coding)",
        "profile": "Main 10",
        "codec_type": "video",
        "codec_tag_string": "hvc1",
        "codec_tag": "0x31637668",
        "width": 1920,
        "height": 1080,
        "coded_width": 1920,
        "coded_height": 1080,
        "has_b_frames": 2,
        "pix_fmt": "yuv420p10le",
        "level": 120,
        "color_range": "tv",
        "color_space": "bt2020nc",
        "color_transfer": "arib-std-b67",
        "color_primaries": "bt2020",
        "chroma_location": "left",
        "refs": 1,
        "view_ids_available": "",
        "view_pos_available": "",
        "id": "0x1",
        "r_frame_rate": "30/1",
        "avg_frame_rate": "30/1",
        "time_base": "1/15360",
        "start_pts": 0,
        "start_time": "0.000000",
        "duration_ts": 107520,
        "duration": "7.000000",
        "bit_rate": "10413285",
        "nb_frames": "210",
        "extradata_size": 2438,
        "disposition": {
          "default": 1,
          "dub": 0,
          "original": 0,
          "comment": 0,
          "lyrics": 0,
          "karaoke": 0,
          "forced": 0,
          "hearing_impaired": 0,
          "visual_impaired": 0,
          "clean_effects": 0,
          "attached_pic": 0,
          "timed_thumbnails": 0,
          "non_diegetic": 0,
          "captions": 0,
          "descriptions": 0,
          "metadata": 0,
          "dependent": 0,
          "still_image": 0,
          "multilayer": 0
        },
        "tags": {
          "language": "und",
          "handler_name": "VideoHandler",
          "vendor_id": "[0][0][0][0]"
        }
      }
    ]
  }
  ```

  </details>

- Comparison
  | Original HDR PQ | Converted HLG using ffmpeg | Converted HLG using main.py | Rewrapped HLG using main.py |
  |---|---|---|---|
  |<video src="https://github.com/user-attachments/assets/2ad463fe-e470-440e-8216-cc9b7902c4e5" placeholder="Test HDR PQ Video" autoplay loop controls muted title="Test HDR PQ Video"></video>|<video src="https://github.com/user-attachments/assets/2b3215cf-fe6a-4dac-9c63-ca3b96df03ee" placeholder="Converted HLG using ffmpeg" autoplay loop controls muted title="Converted HLG using ffmpeg"></video>|<video src="https://github.com/user-attachments/assets/abe5750c-a031-454c-817d-1f6e917d5b4b" placeholder="Converted HLG using main.py" autoplay loop controls muted title="Converted HLG using main.py"></video>|<video src="https://github.com/user-attachments/assets/e9a28ee3-d1bb-4ead-9c67-86549f761022" placeholder="Rewrapped HLG using main.py" autoplay loop controls muted title="Rewrapped HLG using main.py"></video>|

3. HDR (HLG) ➡️ SDR Conversion

- `output/ffmpeg/hlg2sdr.mp4`: Converted to SDR using ffmpeg command:

  ```bash
  ffmpeg -i test_hlg.mp4 -vf "zscale=t=linear:npl=100, format=gbrpf32le, zscale=p=bt709, zscale=t=bt709:m=bt709:r=tv, format=yuv420p" ./output/ffmpeg/hlg2sdr.mp4
  ```

  <details>
    <summary>Video Details from Apple QuickTimePlayer's Video Inspector <span style="font-style: italic;">(Command + I)</span>:</summary>
    
    | Property          | Value               |
    | ----------------- | ------------------- |
    | Color Primaries   | ITU-R BT.709        |
    | Transfer Function | ITU-R BT.709        |
    | YCbCr Matrix      | ITU-R BT.709        |

  </details>

- `output/test_hlg2sdr.mp4`: Converted using `main.py` command:

  ```bash
  python main.py hlg2sdr -i test_hlg.mp4
  # or using uv
  uv run main.py hlg2sdr -i test_hlg.mp4
  ```

  <details>
    <summary>Video Details using <span style="font-style: italic;">ffprobe</span> (same as above command just diff file):</summary>

  ```json
  {
    "streams": [
      {
        "index": 0,
        "codec_name": "h264",
        "codec_long_name": "H.264 / AVC / MPEG-4 AVC / MPEG-4 part 10",
        "profile": "High",
        "codec_type": "video",
        "codec_tag_string": "avc1",
        "codec_tag": "0x31637661",
        "width": 1920,
        "height": 1080,
        "coded_width": 1920,
        "coded_height": 1080,
        "has_b_frames": 2,
        "pix_fmt": "yuv420p",
        "level": 40,
        "color_range": "tv",
        "color_space": "bt709",
        "color_transfer": "bt709",
        "color_primaries": "bt709",
        "chroma_location": "left",
        "field_order": "progressive",
        "refs": 1,
        "is_avc": "true",
        "nal_length_size": "4",
        "id": "0x1",
        "r_frame_rate": "30000/1001",
        "avg_frame_rate": "30000/1001",
        "time_base": "1/30000",
        "start_pts": 990,
        "start_time": "0.033000",
        "duration_ts": 89089,
        "duration": "2.969633",
        "bit_rate": "6882767",
        "bits_per_raw_sample": "8",
        "nb_frames": "89",
        "extradata_size": 49,
        "disposition": {
          "default": 1,
          "dub": 0,
          "original": 0,
          "comment": 0,
          "lyrics": 0,
          "karaoke": 0,
          "forced": 0,
          "hearing_impaired": 0,
          "visual_impaired": 0,
          "clean_effects": 0,
          "attached_pic": 0,
          "timed_thumbnails": 0,
          "non_diegetic": 0,
          "captions": 0,
          "descriptions": 0,
          "metadata": 0,
          "dependent": 0,
          "still_image": 0,
          "multilayer": 0
        },
        "tags": {
          "language": "und",
          "handler_name": "VideoHandler",
          "vendor_id": "[0][0][0][0]"
        }
      }
    ]
  }
  ```

  </details>

- `output/rewrap/test_hlg2sdr_rewrapped.mp4`: Rewrap (convert without using transfer functions, changed metadata) using `main.py` command:

  ```bash
  python main.py rewrap -i test_hlg.mp4 --src hlg --dst sdr
  # or using uv
  uv run main.py rewrap -i test_hlg.mp4 --src hlg --dst sdr
  ```

  <details>
    <summary>Video Details using <span style="font-style: italic;">ffprobe</span> (same as above command just diff file):</summary>

  ```json
  {
    "streams": [
      {
        "index": 0,
        "codec_name": "h264",
        "codec_long_name": "H.264 / AVC / MPEG-4 AVC / MPEG-4 part 10",
        "profile": "High",
        "codec_type": "video",
        "codec_tag_string": "avc1",
        "codec_tag": "0x31637661",
        "width": 1920,
        "height": 1080,
        "coded_width": 1920,
        "coded_height": 1080,
        "has_b_frames": 2,
        "pix_fmt": "yuv420p",
        "level": 40,
        "color_range": "tv",
        "color_space": "bt709",
        "color_transfer": "bt709",
        "color_primaries": "bt709",
        "chroma_location": "left",
        "field_order": "progressive",
        "refs": 1,
        "is_avc": "true",
        "nal_length_size": "4",
        "id": "0x1",
        "r_frame_rate": "30000/1001",
        "avg_frame_rate": "30000/1001",
        "time_base": "1/30000",
        "start_pts": 990,
        "start_time": "0.033000",
        "duration_ts": 89089,
        "duration": "2.969633",
        "bit_rate": "4849657",
        "bits_per_raw_sample": "8",
        "nb_frames": "89",
        "extradata_size": 49,
        "disposition": {
          "default": 1,
          "dub": 0,
          "original": 0,
          "comment": 0,
          "lyrics": 0,
          "karaoke": 0,
          "forced": 0,
          "hearing_impaired": 0,
          "visual_impaired": 0,
          "clean_effects": 0,
          "attached_pic": 0,
          "timed_thumbnails": 0,
          "non_diegetic": 0,
          "captions": 0,
          "descriptions": 0,
          "metadata": 0,
          "dependent": 0,
          "still_image": 0,
          "multilayer": 0
        },
        "tags": {
          "language": "und",
          "handler_name": "VideoHandler",
          "vendor_id": "[0][0][0][0]"
        }
      }
    ]
  }
  ```

  </details>

- Comparison
  | Original HDR HLG | Converted SDR using ffmpeg | Converted SDR using main.py | Rewrap SDR using main.py |
  |---|---|---|---|
  |<video src="https://github.com/user-attachments/assets/3630df24-6a10-4fc7-9649-e35f7980f555" placeholder="Test HDR HLG Video" autoplay loop controls muted title="Test HDR HLG Video"></video>|<video src="https://github.com/user-attachments/assets/a68847e4-37ca-4b39-a00a-ff3215357e50" placeholder="Converted SDR using ffmpeg" autoplay loop controls muted title="Converted SDR using ffmpeg"></video>|<video src="https://github.com/user-attachments/assets/ebcd5e1c-d9ab-44fe-aea4-2542846b5fce" placeholder="Converted SDR using main.py" autoplay loop controls muted title="Converted SDR using main.py"></video>|<video src="https://github.com/user-attachments/assets/51b0728c-10cb-4d3c-ba16-14ca9f21eb23" placeholder="Rewrapped SDR using main.py" autoplay loop controls muted title="Rewrapped SDR using main.py"></video>|

4. HDR (HLG) ➡️ HDR (PQ10) Conversion

- `output/ffmpeg/hlg2pq.mp4`: Converted to HDR (PQ10) using ffmpeg command:

  ```bash
  ffmpeg -i test_hlg.mp4 -vf "zscale=t=smpte2084" -c:v libx265 -crf 20 -preset fast -tag:v hvc1 ./output/ffmpeg/hlg2pq.mp4
  ```

  <details>
    <summary>Video Details from Apple QuickTimePlayer's Video Inspector <span style="font-style: italic;">(Command + I)</span>:</summary>

  | Property          | Value              |
  | ----------------- | ------------------ |
  | Bit Depth         | 10-bit             |
  | HDR Type          | HDR10              |
  | Color Primaries   | ITU-R BT.2020      |
  | Transfer Function | SMPTE ST 2084 (PQ) |
  | YCbCr Matrix      | ITU-R BT.2020      |

  </details>

- `output/test_hlg2pq.mp4`: Converted using `main.py` command:

  ```bash
  python main.py hlg2pq -i test_hlg.mp4
  # or using uv
  uv run main.py hlg2pq -i test_hlg.mp4
  ```

  <details>
    <summary>Video Details using <span style="font-style: italic;">ffprobe</span> (same as above command just diff file):</summary>

  ```json
  {
    "streams": [
      {
        "index": 0,
        "codec_name": "hevc",
        "codec_long_name": "H.265 / HEVC (High Efficiency Video Coding)",
        "profile": "Main 10",
        "codec_type": "video",
        "codec_tag_string": "hvc1",
        "codec_tag": "0x31637668",
        "width": 1920,
        "height": 1080,
        "coded_width": 1920,
        "coded_height": 1080,
        "has_b_frames": 2,
        "pix_fmt": "yuv420p10le",
        "level": 120,
        "color_range": "tv",
        "color_space": "bt2020nc",
        "color_transfer": "smpte2084",
        "color_primaries": "bt2020",
        "chroma_location": "left",
        "refs": 1,
        "view_ids_available": "",
        "view_pos_available": "",
        "id": "0x1",
        "r_frame_rate": "30000/1001",
        "avg_frame_rate": "30000/1001",
        "time_base": "1/30000",
        "start_pts": 990,
        "start_time": "0.033000",
        "duration_ts": 89089,
        "duration": "2.969633",
        "bit_rate": "2574192",
        "nb_frames": "89",
        "extradata_size": 2442,
        "disposition": {
          "default": 1,
          "dub": 0,
          "original": 0,
          "comment": 0,
          "lyrics": 0,
          "karaoke": 0,
          "forced": 0,
          "hearing_impaired": 0,
          "visual_impaired": 0,
          "clean_effects": 0,
          "attached_pic": 0,
          "timed_thumbnails": 0,
          "non_diegetic": 0,
          "captions": 0,
          "descriptions": 0,
          "metadata": 0,
          "dependent": 0,
          "still_image": 0,
          "multilayer": 0
        },
        "tags": {
          "language": "und",
          "handler_name": "VideoHandler",
          "vendor_id": "[0][0][0][0]"
        }
      }
    ]
  }
  ```

  </details>

- `output/rewrap/test_hlg2pq_rewrapped.mp4`: Rewrap (convert without using transfer functions, changed metadata) using `main.py` command:

  ```bash
  python main.py rewrap -i test_hlg.mp4 --src hlg --dst pq
  # or using uv
  uv run main.py rewrap -i test_hlg.mp4 --src hlg --dst pq
  ```

  <details>
    <summary>Video Details using <span style="font-style: italic;">ffprobe</span> (same as above command just diff file):</summary>

  ```json
  {
    "streams": [
      {
        "index": 0,
        "codec_name": "hevc",
        "codec_long_name": "H.265 / HEVC (High Efficiency Video Coding)",
        "profile": "Main 10",
        "codec_type": "video",
        "codec_tag_string": "hvc1",
        "codec_tag": "0x31637668",
        "width": 1920,
        "height": 1080,
        "coded_width": 1920,
        "coded_height": 1080,
        "has_b_frames": 2,
        "pix_fmt": "yuv420p10le",
        "level": 120,
        "color_range": "tv",
        "color_space": "bt2020nc",
        "color_transfer": "smpte2084",
        "color_primaries": "bt2020",
        "chroma_location": "left",
        "refs": 1,
        "view_ids_available": "",
        "view_pos_available": "",
        "id": "0x1",
        "r_frame_rate": "30000/1001",
        "avg_frame_rate": "30000/1001",
        "time_base": "1/30000",
        "start_pts": 990,
        "start_time": "0.033000",
        "duration_ts": 89089,
        "duration": "2.969633",
        "bit_rate": "2855908",
        "nb_frames": "89",
        "extradata_size": 2442,
        "disposition": {
          "default": 1,
          "dub": 0,
          "original": 0,
          "comment": 0,
          "lyrics": 0,
          "karaoke": 0,
          "forced": 0,
          "hearing_impaired": 0,
          "visual_impaired": 0,
          "clean_effects": 0,
          "attached_pic": 0,
          "timed_thumbnails": 0,
          "non_diegetic": 0,
          "captions": 0,
          "descriptions": 0,
          "metadata": 0,
          "dependent": 0,
          "still_image": 0,
          "multilayer": 0
        },
        "tags": {
          "language": "und",
          "handler_name": "VideoHandler",
          "vendor_id": "[0][0][0][0]"
        }
      }
    ]
  }
  ```

  </details>

- Comparison
  | Original HDR HLG | Converted PQ using ffmpeg | Converted PQ using main.py | Rewrapped PQ using main.py |
  |---|---|---|---|
  |<video src="https://github.com/user-attachments/assets/3630df24-6a10-4fc7-9649-e35f7980f555" placeholder="Test HDR HLG Video" autoplay loop controls muted title="Test HDR HLG Video"></video>|<video src="https://github.com/user-attachments/assets/60150f43-fb81-446f-9f85-4ee6f0660224" placeholder="Converted PQ using ffmpeg" autoplay loop controls muted title="Converted PQ using ffmpeg"></video>|<video src="https://github.com/user-attachments/assets/668aea9f-873d-4300-bda2-4a71623be452" placeholder="Converted PQ using main.py" autoplay loop controls muted title="Converted PQ using main.py"></video>|<video src="https://github.com/user-attachments/assets/fa9ef370-9fcf-4e00-9ce6-aea078f96d0b" placeholder="Rewrapped PQ using main.py" autoplay loop controls muted title="Rewrapped PQ using main.py"></video>|

5. SDR ➡️ HDR (PQ10) Conversion

- `output/ffmpeg/sdr2pq.mp4`: Converted to HDR (PQ10) using ffmpeg command:

  ```bash
  ffmpeg -i "test_sdr.mp4" -vf "format=gbrpf32le, zscale=tin=bt709:pin=bt709:t=smpte2084:p=bt2020:m=bt2020nc, format=yuv420p10le" -c:v libx265 -crf 20 -preset fast -tag:v hvc1 ./output/ffmpeg/sdr2pq.mp4
  ```

    <details>
      <summary>Video Details from Apple QuickTimePlayer's Video Inspector <span style="font-style: italic;">(Command + I)</span>:</summary>

  | Property          | Value              |
  | ----------------- | ------------------ |
  | Bit Depth         | 10-bit             |
  | HDR Type          | HDR10              |
  | Color Primaries   | ITU-R BT.2020      |
  | Transfer Function | SMPTE ST 2084 (PQ) |
  | YCbCr Matrix      | ITU-R BT.2020      |

    </details>

- `output/test_sdr2pq.mp4`: Converted using `main.py` command:

  ```bash
  python main.py sdr2pq -i test_sdr.mp4
  # or using uv
  uv run main.py sdr2pq -i test_sdr.mp4
  ```

  <details>
    <summary>Video Details using <span style="font-style: italic;">ffprobe</span> (same as above command just diff file):</summary>

  ```json
  {
    "streams": [
      {
        "index": 0,
        "codec_name": "hevc",
        "codec_long_name": "H.265 / HEVC (High Efficiency Video Coding)",
        "profile": "Main 10",
        "codec_type": "video",
        "codec_tag_string": "hvc1",
        "codec_tag": "0x31637668",
        "width": 1920,
        "height": 1080,
        "coded_width": 1920,
        "coded_height": 1080,
        "has_b_frames": 2,
        "pix_fmt": "yuv420p10le",
        "level": 120,
        "color_range": "tv",
        "color_space": "bt2020nc",
        "color_transfer": "smpte2084",
        "color_primaries": "bt2020",
        "chroma_location": "left",
        "refs": 1,
        "view_ids_available": "",
        "view_pos_available": "",
        "id": "0x1",
        "r_frame_rate": "30/1",
        "avg_frame_rate": "30/1",
        "time_base": "1/15360",
        "start_pts": 0,
        "start_time": "0.000000",
        "duration_ts": 153600,
        "duration": "10.000000",
        "bit_rate": "4456511",
        "nb_frames": "300",
        "extradata_size": 2438,
        "disposition": {
          "default": 1,
          "dub": 0,
          "original": 0,
          "comment": 0,
          "lyrics": 0,
          "karaoke": 0,
          "forced": 0,
          "hearing_impaired": 0,
          "visual_impaired": 0,
          "clean_effects": 0,
          "attached_pic": 0,
          "timed_thumbnails": 0,
          "non_diegetic": 0,
          "captions": 0,
          "descriptions": 0,
          "metadata": 0,
          "dependent": 0,
          "still_image": 0,
          "multilayer": 0
        },
        "tags": {
          "language": "und",
          "handler_name": "VideoHandler",
          "vendor_id": "[0][0][0][0]"
        }
      }
    ]
  }
  ```

  </details>

- `output/rewrap/test_sdr2pq_rewrapped.mp4`: Rewrap (convert without using transfer functions, changed metadata) using `main.py` command:

  ```bash
  python main.py rewrap -i test_sdr.mp4 --src sdr --dst pq
  # or using uv
  uv run main.py rewrap -i test_sdr.mp4 --src sdr --dst pq
  ```

  <details>
    <summary>Video Details using <span style="font-style: italic;">ffprobe</span> (same as above command just diff file):</summary>

  ```json
  {
    "streams": [
      {
        "index": 0,
        "codec_name": "hevc",
        "codec_long_name": "H.265 / HEVC (High Efficiency Video Coding)",
        "profile": "Main 10",
        "codec_type": "video",
        "codec_tag_string": "hvc1",
        "codec_tag": "0x31637668",
        "width": 1920,
        "height": 1080,
        "coded_width": 1920,
        "coded_height": 1080,
        "has_b_frames": 2,
        "pix_fmt": "yuv420p10le",
        "level": 120,
        "color_range": "tv",
        "color_space": "bt2020nc",
        "color_transfer": "smpte2084",
        "color_primaries": "bt2020",
        "chroma_location": "left",
        "refs": 1,
        "view_ids_available": "",
        "view_pos_available": "",
        "id": "0x1",
        "r_frame_rate": "30/1",
        "avg_frame_rate": "30/1",
        "time_base": "1/15360",
        "start_pts": 0,
        "start_time": "0.000000",
        "duration_ts": 153600,
        "duration": "10.000000",
        "bit_rate": "7674006",
        "nb_frames": "300",
        "extradata_size": 2438,
        "disposition": {
          "default": 1,
          "dub": 0,
          "original": 0,
          "comment": 0,
          "lyrics": 0,
          "karaoke": 0,
          "forced": 0,
          "hearing_impaired": 0,
          "visual_impaired": 0,
          "clean_effects": 0,
          "attached_pic": 0,
          "timed_thumbnails": 0,
          "non_diegetic": 0,
          "captions": 0,
          "descriptions": 0,
          "metadata": 0,
          "dependent": 0,
          "still_image": 0,
          "multilayer": 0
        },
        "tags": {
          "language": "und",
          "handler_name": "VideoHandler",
          "vendor_id": "[0][0][0][0]"
        }
      }
    ]
  }
  ```

  </details>

- Comparison
  | Original SDR | Converted PQ using ffmpeg | Converted PQ using main.py | Rewrapped PQ using main.py |
  |---|---|---|---|
  |<video src="https://github.com/user-attachments/assets/44cc7874-e29a-4ccb-b1c3-ee3a3f375e98" placeholder="Test SDR Video" autoplay loop controls muted title="Test SDR Video"></video>|<video src="https://github.com/user-attachments/assets/9377f253-7506-47a1-b0f5-bb337f15fd13" placeholder="Converted PQ using ffmpeg" autoplay loop controls muted title="Converted PQ using ffmpeg"></video>|<video src="https://github.com/user-attachments/assets/c07aed06-eab7-497e-90c1-d41f69d1d2b7" placeholder="Converted PQ using main.py" autoplay loop controls muted title="Converted PQ using main.py"></video>|<video src="https://github.com/user-attachments/assets/ac61e5cf-e5eb-47e9-a6f6-15f168168a1f" placeholder="Rewrapped PQ using main.py" autoplay loop controls muted title="Rewrapped PQ using main.py"></video>|

6. SDR ➡️ HDR (HLG) Conversion

- `output/ffmpeg/sdr2hlg.mp4`: Converted to HDR (HLG) using ffmpeg command:

  ```bash
  ffmpeg -i "test_sdr.mp4" -vf "format=gbrpf32le, zscale=tin=bt709:pin=bt709:t=arib-std-b67:p=bt2020:m=bt2020nc, format=yuv420p10le" -c:v libx265 -crf 20 -preset fast -tag:v hvc1 ./output/ffmpeg/sdr2hlg.mp4
  ```

    <details>
      <summary>Video Details from Apple QuickTimePlayer's Video Inspector <span style="font-style: italic;">(Command + I)</span>:</summary>

  | Property          | Value             |
  | ----------------- | ----------------- |
  | Bit Depth         | 10-bit            |
  | HDR Type          | HLG               |
  | Color Primaries   | ITU-R BT.2020     |
  | Transfer Function | ITU-R BT.2100 HLG |
  | YCbCr Matrix      | ITU-R BT.2020     |

    </details>

- `output/test_sdr2hlg.mp4`: Converted using `main.py` command:

  ```bash
  python main.py sdr2hlg -i test_sdr.mp4
  # or using uv
  uv run main.py sdr2hlg -i test_sdr.mp4
  ```

  <details>
    <summary>Video Details using <span style="font-style: italic;">ffprobe</span> (same as above command just diff file):</summary>

  ```json
  {
    "streams": [
      {
        "index": 0,
        "codec_name": "hevc",
        "codec_long_name": "H.265 / HEVC (High Efficiency Video Coding)",
        "profile": "Main 10",
        "codec_type": "video",
        "codec_tag_string": "hvc1",
        "codec_tag": "0x31637668",
        "width": 1920,
        "height": 1080,
        "coded_width": 1920,
        "coded_height": 1080,
        "has_b_frames": 2,
        "pix_fmt": "yuv420p10le",
        "level": 120,
        "color_range": "tv",
        "color_space": "bt2020nc",
        "color_transfer": "arib-std-b67",
        "color_primaries": "bt2020",
        "chroma_location": "left",
        "refs": 1,
        "view_ids_available": "",
        "view_pos_available": "",
        "id": "0x1",
        "r_frame_rate": "30/1",
        "avg_frame_rate": "30/1",
        "time_base": "1/15360",
        "start_pts": 0,
        "start_time": "0.000000",
        "duration_ts": 153600,
        "duration": "10.000000",
        "bit_rate": "5601019",
        "nb_frames": "300",
        "extradata_size": 2438,
        "disposition": {
          "default": 1,
          "dub": 0,
          "original": 0,
          "comment": 0,
          "lyrics": 0,
          "karaoke": 0,
          "forced": 0,
          "hearing_impaired": 0,
          "visual_impaired": 0,
          "clean_effects": 0,
          "attached_pic": 0,
          "timed_thumbnails": 0,
          "non_diegetic": 0,
          "captions": 0,
          "descriptions": 0,
          "metadata": 0,
          "dependent": 0,
          "still_image": 0,
          "multilayer": 0
        },
        "tags": {
          "language": "und",
          "handler_name": "VideoHandler",
          "vendor_id": "[0][0][0][0]"
        }
      }
    ]
  }
  ```

  </details>

- `output/rewrap/test_sdr2hlg_rewrapped.mp4`: Rewrap (convert without using transfer functions, changed metadata) using `main.py` command:

  ```bash
  python main.py rewrap -i test_sdr.mp4 --src sdr --dst hlg
  # or using uv
  uv run main.py rewrap -i test_sdr.mp4 --src sdr --dst hlg
  ```

  <details>
    <summary>Video Details using <span style="font-style: italic;">ffprobe</span> (same as above command just diff file):</summary>

  ```json
  {
    "streams": [
      {
        "index": 0,
        "codec_name": "hevc",
        "codec_long_name": "H.265 / HEVC (High Efficiency Video Coding)",
        "profile": "Main 10",
        "codec_type": "video",
        "codec_tag_string": "hvc1",
        "codec_tag": "0x31637668",
        "width": 1920,
        "height": 1080,
        "coded_width": 1920,
        "coded_height": 1080,
        "has_b_frames": 2,
        "pix_fmt": "yuv420p10le",
        "level": 120,
        "color_range": "tv",
        "color_space": "bt2020nc",
        "color_transfer": "arib-std-b67",
        "color_primaries": "bt2020",
        "chroma_location": "left",
        "refs": 1,
        "view_ids_available": "",
        "view_pos_available": "",
        "id": "0x1",
        "r_frame_rate": "30/1",
        "avg_frame_rate": "30/1",
        "time_base": "1/15360",
        "start_pts": 0,
        "start_time": "0.000000",
        "duration_ts": 153600,
        "duration": "10.000000",
        "bit_rate": "7674006",
        "nb_frames": "300",
        "extradata_size": 2438,
        "disposition": {
          "default": 1,
          "dub": 0,
          "original": 0,
          "comment": 0,
          "lyrics": 0,
          "karaoke": 0,
          "forced": 0,
          "hearing_impaired": 0,
          "visual_impaired": 0,
          "clean_effects": 0,
          "attached_pic": 0,
          "timed_thumbnails": 0,
          "non_diegetic": 0,
          "captions": 0,
          "descriptions": 0,
          "metadata": 0,
          "dependent": 0,
          "still_image": 0,
          "multilayer": 0
        },
        "tags": {
          "language": "und",
          "handler_name": "VideoHandler",
          "vendor_id": "[0][0][0][0]"
        }
      }
    ]
  }
  ```

  </details>

- Comparison
  | Original SDR | Converted HLG using ffmpeg | Converted HLG using main.py | Rewrapped HLG using main.py |
  |---|---|---|---|
  |<video src="https://github.com/user-attachments/assets/44cc7874-e29a-4ccb-b1c3-ee3a3f375e98" placeholder="Test SDR Video" autoplay loop controls muted title="Test SDR Video"></video>|<video src="https://github.com/user-attachments/assets/e8363f86-6e44-4d0f-8a21-ae0974a62b7c" placeholder="Converted HLG using ffmpeg" autoplay loop controls muted title="Converted HLG using ffmpeg"></video>|<video src="https://github.com/user-attachments/assets/aa50be80-3783-4686-8ac9-bea71f14675a" placeholder="Converted HLG using main.py" autoplay loop controls muted title="Converted HLG using main.py"></video>|<video src="https://github.com/user-attachments/assets/60809e7e-1fab-4979-97bd-6d6279b5e963" placeholder="Rewrapped HLG using main.py" autoplay loop controls muted title="Rewrapped HLG using main.py"></video>|

# References

https://www.itu.int/rec/R-REC-BT.2100-3-202502-I/en

https://www.itu.int/rec/R-REC-BT.709-6-201506-I/en

https://www.itu.int/rec/R-REC-BT.1886-0-201103-I/en

https://www.itu.int/rec/R-REC-BT.2087/en

https://www.itu.int/rec/R-REC-BT.2020-2-201510-I/en

https://www.itu.int/pub/R-REP-BT.2408-8-2024
