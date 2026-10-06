"""Command-line entry point for Phase-1 data understanding."""

from __future__ import annotations

import argparse
from pathlib import Path

from .report import analyze_csv, export_csv_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="CrimeMapAI Phase-1 CSV data understanding"
    )
    parser.add_argument(
        "csv",
        nargs="+",
        help="One or more CSV files to analyze independently.",
    )
    parser.add_argument(
        "--output",
        default="reports/tables/data_understanding",
        help="Directory for machine-readable diagnostic tables.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()

    for path in args.csv:
        print("=" * 100)
        print(f"DATASET: {path}")
        print("=" * 100)

        report = analyze_csv(path)
        summary = report["summary"]

        print(f"Rows: {summary.rows:,}")
        print(f"Columns: {summary.columns:,}")
        print(f"Duplicates: {summary.duplicate_rows:,}")
        print(f"Missing cells: {summary.missing_cells_pct:.2f}%")
        print(f"Encoding: {report['encoding']}")

        written = export_csv_report(report, args.output)

        print("Written:")
        for item in written:
            print(f"  - {item}")


if __name__ == "__main__":
    main()
