from pathlib import Path

import pytest

from server.validation.qa_test_data import (
    DEFAULT_DATA_PATH,
    QATestCase,
    QATestDataValidationError,
    validate_qa_test_data,
)

BUNDLED = (
    Path(__file__).resolve().parents[1]
    / "server"
    / "validation"
    / "data"
    / "qa_test_data.xlsx"
)


def test_bundled_data_passes_validation():
    report = validate_qa_test_data(BUNDLED)
    assert report.ok, report.summary()
    assert len(report.valid) == 5
    assert [c.id for c in report.valid] == [
        "TC-001",
        "TC-002",
        "TC-003",
        "TC-004",
        "TC-005",
    ]


def test_default_path_points_at_bundled_file():
    assert Path(DEFAULT_DATA_PATH) == BUNDLED


@pytest.mark.parametrize("status", ["Pass", "Fail", "Blocked", "Not Run"])
def test_valid_statuses_accepted(status):
    case = QATestCase(id="TC-042", title="Some test", status=status)
    assert case.status == status


def test_invalid_status_rejected():
    with pytest.raises(Exception):
        QATestCase(id="TC-042", title="Some test", status="Done")


def test_invalid_id_rejected():
    with pytest.raises(Exception):
        QATestCase(id="042", title="Some test", status="Pass")


def test_blank_title_rejected():
    with pytest.raises(Exception):
        QATestCase(id="TC-042", title="   ", status="Pass")


def test_missing_workbook_raises():
    with pytest.raises(QATestDataValidationError):
        validate_qa_test_data("does-not-exist.xlsx")
