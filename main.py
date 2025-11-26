import argparse
import os
import sys

from converter import (
    HLG,
    HLG2PQ,
    HLG2SDR,
    PQ,
    PQ2HLG,
    PQ2SDR,
    SDR,
    SDR2HLG,
    SDR2PQ,
    Rewrap,
)

CONVERTERS = {
    "sdr2pq": SDR2PQ,
    "sdr2hlg": SDR2HLG,
    "pq2sdr": PQ2SDR,
    "hlg2sdr": HLG2SDR,
    "pq2hlg": PQ2HLG,
    "hlg2pq": HLG2PQ,
}

FORMATS = {
    "sdr": SDR,
    "pq": PQ,
    "hlg": HLG,
}


def parse_args():
    parser = argparse.ArgumentParser(
        description="Convert video between SDR, PQ (HDR10), and HLG formats",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py sdr2pq -i test_sdr.mp4 -o test_sdr2pq.mp4
  uv run main.py sdr2pq -i test_sdr.mp4 -o test_sdr2pq.mp4
  python main.py pq2sdr -i test_pq.mp4
  uv run main.py pq2sdr -i test_pq.mp4
  python main.py rewrap -i input.mp4 --src pq --dst hlg
  uv run main.py rewrap -i input.mp4 --src pq --dst hlg
  python main.py list
  uv run main.py list
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # List command
    subparsers.add_parser("list", help="List available conversions")

    for name in CONVERTERS:
        sub = subparsers.add_parser(name, help=f"Convert {name.replace('2', ' -> ')}")
        sub.add_argument("-i", "--input", required=True, help="Input video file")
        sub.add_argument("-o", "--output", help="Output video file (optional)")

    # Rewrap command (no transfer conversion)
    rewrap = subparsers.add_parser(
        "rewrap", help="Rewrap without transfer conversion (for comparison)"
    )
    rewrap.add_argument("-i", "--input", required=True, help="Input video file")
    rewrap.add_argument("-o", "--output", help="Output video file (optional)")
    rewrap.add_argument(
        "--src",
        choices=FORMATS.keys(),
        default="pq",
        help="Source format (default: pq)",
    )
    rewrap.add_argument(
        "--dst",
        choices=FORMATS.keys(),
        default="hlg",
        help="Destination format (default: hlg)",
    )

    return parser.parse_args()


def main():
    args = parse_args()

    if args.command is None:
        print("No command specified. Use --help for usage.")
        sys.exit(1)

    if args.command == "list":
        print("Available conversions:")
        print()
        for name in CONVERTERS:
            src, dst = name.split("2")
            print(f"  {name:12} {src.upper():4} -> {dst.upper()}")
        print(f"  {'rewrap':12} Copy pixels, change metadata only")
        print()
        print("Formats:")
        print("  sdr  - BT.709, 8-bit")
        print("  pq   - BT.2100 PQ (HDR10), 10-bit")
        print("  hlg  - BT.2100 HLG, 10-bit")
        return

    # Validate input file
    if not os.path.exists(args.input):
        print(f"Error: Input file not found: {args.input}")
        sys.exit(1)

    # Generate output path if not specified
    output = args.output
    if output is None:
        output = f"output/test_{args.command}.mp4"

    output_dir = os.path.dirname(output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    if args.command == "rewrap":
        converter = Rewrap(
            args.input,
            output,
            src_fmt=FORMATS[args.src],
            dst_fmt=FORMATS[args.dst],
        )
    elif args.command in CONVERTERS:
        converter_cls = CONVERTERS[args.command]
        converter = converter_cls(args.input, output)
    else:
        print(f"Unknown command: {args.command}")
        sys.exit(1)

    converter.process()


if __name__ == "__main__":
    main()
