"""One-command runner for the ScanSight project."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"


def _ensure_import_path() -> None:
    src_path = str(SRC)
    if src_path not in sys.path:
        sys.path.insert(0, src_path)

    # Auto-detect local virtualenv site-packages if available
    venv_dir = ROOT / ".venv"
    if venv_dir.exists():
        win_site = venv_dir / "Lib" / "site-packages"
        if win_site.exists() and str(win_site) not in sys.path:
            sys.path.insert(0, str(win_site))
        lib_dir = venv_dir / "lib"
        if lib_dir.exists():
            for p in lib_dir.glob("python*/site-packages"):
                if str(p) not in sys.path:
                    sys.path.insert(0, str(p))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the ScanSight document scanner (Browser UI or Terminal CLI)."
    )
    parser.add_argument(
        "-i",
        "--input",
        help="Path to an input document image.",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        default="outputs",
        help="Directory where output files will be saved (default: outputs).",
    )
    parser.add_argument(
        "-c",
        "--cli",
        action="store_true",
        help="Run the terminal scanner interface and exit instead of starting the browser UI.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output quality analysis report in JSON format in CLI mode.",
    )
    parser.add_argument(
        "--run-tests",
        action="store_true",
        help="Run unit tests before starting.",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host for the browser upload UI (default: 127.0.0.1).",
    )
    parser.add_argument(
        "--port",
        default=8000,
        type=int,
        help="Port for the browser upload UI (default: 8000).",
    )
    return parser


def run_tests() -> int:
    print("\nRunning tests...")
    env = os.environ.copy()
    existing_path = env.get("PYTHONPATH")
    env["PYTHONPATH"] = str(SRC) if not existing_path else f"{SRC}{os.pathsep}{existing_path}"

    venv_python_win = ROOT / ".venv" / "Scripts" / "python.exe"
    venv_python_posix = ROOT / ".venv" / "bin" / "python"
    if venv_python_win.exists():
        python_bin = str(venv_python_win)
    elif venv_python_posix.exists():
        python_bin = str(venv_python_posix)
    else:
        python_bin = sys.executable

    completed = subprocess.run(
        [python_bin, "-m", "unittest", "discover", "-s", "tests"],
        cwd=ROOT,
        env=env,
        check=False,
    )
    return completed.returncode



def run_scan(input_path: Path | None, output_dir: str, print_json: bool = False) -> int:
    from scansight.cli import print_cli_report, run
    from scripts.generate_sample import create_sample

    try:
        selected_input = input_path if input_path else create_sample(ROOT / "samples" / "sample_document.jpg")
        outputs = run(selected_input, output_dir)
        quality = outputs["quality"]
        print_cli_report(selected_input, outputs, quality, print_json=print_json)  # type: ignore[arg-type]
        return 0
    except FileNotFoundError as e:
        print(f"\nError: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"\nError processing document scan: {e}", file=sys.stderr)
        return 1


def main() -> int:
    _ensure_import_path()

    args = build_parser().parse_args()
    input_path = Path(args.input) if args.input else None

    if args.run_tests:
        test_status = run_tests()
        if test_status != 0:
            return test_status

    if args.cli:
        return run_scan(input_path, args.output_dir, print_json=args.json)

    if input_path:
        scan_status = run_scan(input_path, args.output_dir, print_json=args.json)
        if scan_status != 0:
            return scan_status

    from scansight.web import serve

    serve(args.host, args.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

