"""Command-line interface for ScanSight."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .io_utils import read_image, write_image
from .quality import QualityReport, analyze_quality
from .report import create_visual_report, save_json_report
from .scanner import scan_document


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="ScanSight: Automatic Document Scanner and Quality Analyzer CLI"
    )
    parser.add_argument(
        "-i",
        "--input",
        help="Path to an input document photo. Uses sample document if omitted.",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        default="outputs",
        help="Directory for generated outputs (default: outputs).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output quality report in JSON format.",
    )
    return parser


def run(input_path: str | Path, output_dir: str | Path = "outputs") -> dict[str, object]:
    path_obj = Path(input_path)
    image = read_image(path_obj)
    result = scan_document(image)
    quality = analyze_quality(result.warped)

    output_root = Path(output_dir)
    output_root.mkdir(parents=True, exist_ok=True)

    scanned_path = write_image(output_root / "scanned_document.png", result.enhanced)
    report_image_path = create_visual_report(result, quality, output_root / "visual_report.png")
    report_json_path = save_json_report(quality, output_root / "quality_report.json")

    return {
        "scanned_document": scanned_path,
        "visual_report": report_image_path,
        "quality_report": report_json_path,
        "quality": quality,
    }


def print_cli_report(
    input_path: Path,
    outputs: dict[str, object],
    quality: QualityReport,
    print_json: bool = False,
) -> None:
    if print_json:
        print(json.dumps(quality.to_dict(), indent=2))
        return

    status_str = "[PASS] Acceptable Quality" if quality.passed else "[REVIEW] Review Recommended"
    scanned = outputs["scanned_document"]
    visual = outputs["visual_report"]
    quality_file = outputs["quality_report"]

    print("=" * 64)
    print("       ScanSight: Automatic Document Scanner & Quality Engine      ")
    print("=" * 64)
    print(f" Input Image      : {input_path}")
    print(f" Output Directory : {Path(scanned).parent.resolve()}")
    print("-" * 64)
    print(" Generated Output Files:")
    print(f"  * Scanned Document : {scanned}")
    print(f"  * Visual Report    : {visual}")
    print(f"  * Quality JSON     : {quality_file}")
    print("-" * 64)
    print(" Quality Analysis Results:")
    print(f"  * Overall Status   : {status_str}")
    print(f"  * Brightness       : {quality.brightness:.2f} / 255.0")
    print(f"  * Contrast         : {quality.contrast:.2f}")
    print(f"  * Sharpness        : {quality.sharpness:.2f}")
    print(f"  * Estimated Skew   : {quality.skew_degrees:.2f} deg")
    print("-" * 64)
    print(" Feedback & Recommendations:")
    for msg in quality.messages:
        prefix = "  [+]" if quality.passed else "  [!]"
        print(f"{prefix} {msg}")
    print("=" * 64)



def main() -> int:
    args = build_parser().parse_args()
    input_path = args.input

    if not input_path:
        root_dir = Path(__file__).resolve().parents[2]
        sample_path = root_dir / "samples" / "sample_document.jpg"
        if sample_path.exists():
            input_path = str(sample_path)
        else:
            try:
                from scripts.generate_sample import create_sample
                input_path = str(create_sample(sample_path))
            except Exception:
                print("Error: No input image specified and could not locate sample document.", file=sys.stderr)
                return 1

    try:
        outputs = run(input_path, args.output_dir)
        quality: QualityReport = outputs["quality"]  # type: ignore[assignment]
        print_cli_report(Path(input_path), outputs, quality, print_json=args.json)
        return 0
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error processing image: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())


