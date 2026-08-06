"""Validation for QA test-case data supplied as an Excel workbook.

The workbook is expected to contain a sheet with the columns ``ID``,
``Title`` and ``Status``. Each populated row describes a single QA test
case. This module loads those rows, validates them against a Pydantic
schema and reports any problems. Blank spacer rows and trailing footnote
rows (whose first cell starts with ``Note:``) are ignored.

Run it directly to validate the bundled sample workbook::

    python -m server.validation.qa_test_data
    python -m server.validation.qa_test_data path/to/other.xlsx
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from pathlib import Path

from openpyxl import load_workbook
from pydantic import BaseModel, Field, ValidationError, field_validator

REQUIRED_COLUMNS = ("ID", "Title", "Status")
ALLOWED_STATUSES = ("Pass", "Fail", "Blocked", "Not Run")
ID_PATTERN = r"^TC-\d{3}$"

DEFAULT_DATA_PATH = Path(__file__).resolve().parent / "data" / "qa_test_data.xlsx"


class QATestDataValidationError(Exception):
    """Raised when the workbook itself cannot be read or is structurally invalid."""


class QATestCase(BaseModel):
    """A single QA test case row."""

    id: str = Field(..., pattern=ID_PATTERN)
    title: str = Field(..., min_length=1)
    status: str

    @field_validator("title")
    @classmethod
    def _title_not_blank(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("title must not be blank")
        return cleaned

    @field_validator("status")
    @classmethod
    def _status_allowed(cls, value: str) -> str:
        cleaned = value.strip()
        if cleaned not in ALLOWED_STATUSES:
            allowed = ", ".join(ALLOWED_STATUSES)
            raise ValueError(f"status must be one of: {allowed}")
        return cleaned


@dataclass
class RowError:
    """A validation problem tied to a specific worksheet row."""

    row: int
    id: str | None
    messages: list[str]


@dataclass
class ValidationReport:
    """The outcome of validating a QA test-data workbook."""

    valid: list[QATestCase] = field(default_factory=list)
    errors: list[RowError] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors

    def summary(self) -> str:
        total = len(self.valid) + len(self.errors)
        lines = [
            f"Validated {total} test case row(s): "
            f"{len(self.valid)} valid, {len(self.errors)} invalid."
        ]
        for err in self.errors:
            ident = err.id or "<no id>"
            for message in err.messages:
                lines.append(f"  Row {err.row} ({ident}): {message}")
        return "\n".join(lines)


def _clean(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _is_test_case_row(id_value: str) -> bool:
    if not id_value:
        return False
    if id_value.strip().lower().startswith("note"):
        return False
    return True


def load_qa_rows(path: str | Path) -> list[tuple[int, dict]]:
    """Read populated test-case rows from the workbook.

    Returns a list of ``(worksheet_row_number, raw_field_dict)`` tuples,
    skipping the header, blank spacer rows and footnote rows.
    """

    path = Path(path)
    if not path.exists():
        raise QATestDataValidationError(f"workbook not found: {path}")

    workbook = load_workbook(path, read_only=True, data_only=True)
    try:
        sheet = workbook.active
        rows = sheet.iter_rows(values_only=True)
        try:
            header_cells = next(rows)
        except StopIteration:
            raise QATestDataValidationError("workbook contains no rows")

        header = [_clean(cell) for cell in header_cells]
        missing = [col for col in REQUIRED_COLUMNS if col not in header]
        if missing:
            raise QATestDataValidationError(
                f"missing required column(s): {', '.join(missing)}"
            )
        index = {col: header.index(col) for col in REQUIRED_COLUMNS}

        records: list[tuple[int, dict]] = []
        for row_number, row in enumerate(rows, start=2):
            def cell(col: str) -> str:
                pos = index[col]
                return _clean(row[pos]) if pos < len(row) else ""

            id_value = cell("ID")
            if not _is_test_case_row(id_value):
                continue
            records.append(
                (
                    row_number,
                    {
                        "id": id_value,
                        "title": cell("Title"),
                        "status": cell("Status"),
                    },
                )
            )
        return records
    finally:
        workbook.close()


def validate_qa_test_data(path: str | Path = DEFAULT_DATA_PATH) -> ValidationReport:
    """Validate every test-case row in the workbook and return a report."""

    rows = load_qa_rows(path)
    if not rows:
        raise QATestDataValidationError("no test case rows found in workbook")

    report = ValidationReport()
    seen_ids: dict[str, int] = {}
    for row_number, raw in rows:
        try:
            case = QATestCase(**raw)
        except ValidationError as exc:
            messages = [
                f"{'.'.join(str(part) for part in err['loc']) or 'row'}: {err['msg']}"
                for err in exc.errors()
            ]
            report.errors.append(
                RowError(row=row_number, id=(raw.get("id") or None), messages=messages)
            )
            continue

        if case.id in seen_ids:
            report.errors.append(
                RowError(
                    row=row_number,
                    id=case.id,
                    messages=[f"duplicate ID (first seen on row {seen_ids[case.id]})"],
                )
            )
            continue

        seen_ids[case.id] = row_number
        report.valid.append(case)

    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate QA test-case data in an Excel (.xlsx) workbook."
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=str(DEFAULT_DATA_PATH),
        help="Path to the QA test data .xlsx workbook (defaults to the bundled sample).",
    )
    args = parser.parse_args(argv)

    try:
        report = validate_qa_test_data(args.path)
    except QATestDataValidationError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print(report.summary())
    return 0 if report.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
