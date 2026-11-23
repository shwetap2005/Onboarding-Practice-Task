# HPO Term Loader

## 1. Overview

The HPO Term Loader is a Python command-line application that downloads and processes the Human Phenotype Ontology (HPO) JSON data.

It extracts valid HPO terms and generates a clean CSV lookup table containing:

- `hpo_id`
- `term_name`
- `is_obsolete`

The application also supports loading terms from a local JSON file and optionally storing them in an SQLite database.

## 2. Project Structure

```text
Task-2/
├── hpo_loader.py
├── requirements.txt
├── README.md
├── TEST-REPORT.md
├── tests/
│   ├── __init__.py
│   ├── test_hpo_loader.py
│   └── fixtures/
│       └── sample_hp.json
└── screenshots/
```

## 3. Requirements

- Python 3.11 or later
- pip
- Internet connection for downloading the official HPO JSON file

## 4. Setup Instructions

### Create and activate a virtual environment

```bash
py -3.11 -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### Install dependencies

```bash
python -m pip install -r requirements.txt
```

## 5. Running the Application

### Download official HPO data

```bash
python hpo_loader.py
```

The application downloads the official HPO JSON file and generates `hpo_terms.csv`.

### Use a local JSON file

```bash
python hpo_loader.py --input tests/fixtures/sample_hp.json
```

### Store data in SQLite

```bash
python hpo_loader.py --sqlite hpo.db
```

### Use local JSON input with SQLite

```bash
python hpo_loader.py --input tests/fixtures/sample_hp.json --sqlite hpo.db
```

## 6. Output

The generated `hpo_terms.csv` contains the following columns:

| Column | Description |
|---|---|
| hpo_id | Converted HPO identifier |
| term_name | Name of the phenotype term |
| is_obsolete | Whether the term is deprecated |

The application prints:
- Total number of extracted terms
- Number of obsolete terms
- Time taken to complete processing

## 7. Running Tests

Run all automated tests:

```bash
python -m pytest -v
```

Run tests with code coverage:

```bash
python -m pytest --cov=hpo_loader --cov-report=term-missing
```

The current test suite contains 10 passing tests and achieves 89% code coverage.

## 8. Assumptions

1. The official HPO JSON structure contains the ontology data under `graphs[0].nodes`.
2. Only nodes with `type` equal to `CLASS` and an HPO identifier containing `HP_` are processed.
3. Nodes without a label (`lbl`) are ignored.
4. The HPO identifier is converted from `HP_0001250` to `HP:0001250`.
5. A term is considered obsolete when `meta.deprecated` is `true`. Otherwise, it is considered non-obsolete.
6. Duplicate HPO identifiers are removed using the identifier as the unique key. If duplicates occur, the last occurrence is retained.
7. CSV records are sorted by HPO ID.
8. The SQLite table uses `hpo_id` as its primary key, and `INSERT OR REPLACE` prevents duplicate records on repeated runs.
9. The generated CSV file is written to the current working directory.

## 9. Error Handling

- Download failures are reported with a clear error message.
- Local JSON file reading errors are handled.
- Processing and SQLite errors are reported without exposing a raw traceback.

## 10. Test Report

Refer to [TEST-REPORT.md](TEST-REPORT.md) for automated test results and code coverage details.
