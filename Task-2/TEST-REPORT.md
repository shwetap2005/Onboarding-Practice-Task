# Task 2 – HPO Term Loader Test Report

## 1. Testing Summary

- Testing framework: pytest
- Python version: 3.11.9
- Automated test cases: 10
- Passed: 10
- Failed: 0
- Code coverage: 89%
- Required coverage: 80%
- Manual test cases: 9

## 2. Automated Test Results

| Test | Description | Result |
|---|---|---|
| T1 | Normal HPO node and ID conversion | PASS |
| T2 | Node without label is skipped | PASS |
| T3 | Non-HPO GO node is skipped | PASS |
| T4 | Non-CLASS node is skipped | PASS |
| T5 | Deprecated node marked obsolete | PASS |
| T6 | Duplicate HPO IDs removed | PASS |
| T7 | Terms sorted by HPO ID | PASS |
| T8 | Download failure handled without traceback | PASS |
| T9 | SQLite loading twice creates no duplicates | PASS |
| Additional | CSV columns and output validation | PASS |

## 3. Code Coverage

Command:

`python -m pytest --cov=hpo_loader --cov-report=term-missing`

Results:
- Statements: 81
- Missed statements: 9
- Coverage: 89%

The achieved coverage exceeds the required minimum of 80%.

## 4. Manual Test Results

| Test | Description | Result |
|---|---|---|
| M1 | Normal online execution | PASS |
| M2 | CSV header and sorted records inspection | PASS |
| M3 | HP:0001250 – Seizure lookup | PASS |
| M4 | HP:0000118 – Phenotypic abnormality lookup | PASS |
| M5 | Obsolete terms verification | PASS |
| M6 | Offline download failure handling | PASS |
| M7 | Repeat-run CSV consistency | PASS |
| M8 | Local JSON input | PASS |
| M9 | SQLite repeat-run and duplicate prevention | PASS |

## 5. Important Observations

- Official HPO data produced 20,482 terms.
- 588 terms were identified as obsolete.
- The generated CSV contained the required columns.
- Local JSON processing produced 3 valid terms, including 1 obsolete term.
- Repeated SQLite loading resulted in 3 records, without duplicates.
- Offline download failure produced a clear error message without a traceback.

## 6. Screenshots

The following manual testing screenshots are stored in the `screenshots/` directory:

1. M1_online_execution.png
2. M2_csv_output.png
3. M3_seizure_lookup.png
4. M4_phenotypic_abnormality_lookup.png
5. M5_obsolete_terms.png
6. M6_offline_error.png
7. M7_repeat_run_consistency.png
8. M8_local_json_input.png
9. M9_sqlite_repeat_run.png

## 7. Conclusion

The HPO Term Loader successfully passed all 10 automated tests and the 9 manual test scenarios. It achieved 89% code coverage, exceeding the required 80%.

The application correctly handles HPO data extraction, identifier conversion, obsolete-term detection, duplicate removal, sorting, CSV generation, local JSON input, download failures, and SQLite storage.
