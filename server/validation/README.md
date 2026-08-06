# QA test-data validation

Validates a QA test-case workbook (`.xlsx`) against a Pydantic schema.

The workbook must have a sheet with the columns **ID**, **Title** and
**Status**. Each populated row is validated:

- `ID` matches `TC-###` (e.g. `TC-001`) and is unique
- `Title` is non-empty
- `Status` is one of `Pass`, `Fail`, `Blocked`, `Not Run`

Blank spacer rows and trailing `Note:` footnote rows are ignored.

## Usage

```bash
# validate the bundled sample workbook
python -m server.validation.qa_test_data

# validate another workbook
python -m server.validation.qa_test_data path/to/workbook.xlsx
```

Exit codes: `0` all rows valid, `1` one or more invalid rows, `2` the
workbook could not be read.

## Data

`data/qa_test_data.xlsx` is the bundled sample workbook used by the tests.
