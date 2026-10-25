"""Clean a CSV from the terminal without using a notebook."""
from __future__ import annotations

import argparse
from pathlib import Path

from cleaning import clean_csv_text


def main() -> None:
    parser = argparse.ArgumentParser(description="Clean a CSV using Pandas (no Jupyter Notebook required).")
    parser.add_argument("input_csv", help="Path to the original CSV file")
    parser.add_argument("--output", default="outputs/cleaned_dataset.csv", help="Destination for cleaned CSV")
    parser.add_argument("--report", default="outputs/cleaning_report.txt", help="Destination for audit report")
    args = parser.parse_args()

    input_path = Path(args.input_csv)
    if not input_path.is_file():
        parser.error(f"Input file not found: {input_path}")
    try:
        text = input_path.read_text(encoding="utf-8-sig")
        result = clean_csv_text(text)
    except (UnicodeDecodeError, ValueError) as exc:
        parser.error(str(exc))

    output_path = Path(args.output)
    report_path = Path(args.report)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(result["cleaned_csv"], encoding="utf-8", newline="")
    report_path.write_text(result["report_text"], encoding="utf-8")

    summary = result["summary"]
    print("\nCLEARCUT — DATA CLEANING COMPLETE")
    print("=" * 36)
    print(f"Input file             : {input_path}")
    print(f"Rows before / after    : {summary['original_rows']} / {summary['cleaned_rows']}")
    print(f"Columns                : {summary['columns']}")
    print(f"Missing cells before   : {summary['missing_before']}")
    print(f"Missing cells after    : {summary['missing_after']}")
    print(f"Duplicate rows removed : {summary['duplicates_removed']}")
    print(f"Empty rows removed     : {summary['empty_rows_removed']}")
    print(f"Data-type corrections  : {len(summary['type_changes'])}")
    print(f"Cleaned CSV saved to   : {output_path}")
    print(f"Audit report saved to  : {report_path}\n")


if __name__ == "__main__":
    main()
