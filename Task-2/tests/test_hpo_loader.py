import csv
import json
import sqlite3
from pathlib import Path

import pytest
import requests

import hpo_loader


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "sample_hp.json"


@pytest.fixture
def sample_data():
    """Load the small sample HPO JSON fixture."""
    with open(FIXTURE_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def test_normal_hpo_node_and_id_conversion(sample_data):
    """T1: A valid HPO node should have its ID converted correctly."""
    terms = hpo_loader.extract_hpo_terms(sample_data)

    seizure = next(term for term in terms if term["hpo_id"] == "HP:0001250")

    assert seizure["term_name"] == "Seizure"
    assert seizure["is_obsolete"] is False


def test_node_without_label_is_skipped(sample_data):
    """T2: Nodes without a label should not be included."""
    terms = hpo_loader.extract_hpo_terms(sample_data)

    hpo_ids = [term["hpo_id"] for term in terms]

    assert "HP:0000099" not in hpo_ids


def test_non_hpo_node_is_skipped(sample_data):
    """T3: GO nodes should not be included."""
    terms = hpo_loader.extract_hpo_terms(sample_data)

    hpo_ids = [term["hpo_id"] for term in terms]

    assert all(not hpo_id.startswith("GO:") for hpo_id in hpo_ids)


def test_non_class_node_is_skipped(sample_data):
    """T4: Nodes whose type is not CLASS should be skipped."""
    terms = hpo_loader.extract_hpo_terms(sample_data)

    hpo_ids = [term["hpo_id"] for term in terms]

    assert "HP:0000001" not in hpo_ids


def test_deprecated_node_is_obsolete(sample_data):
    """T5: Deprecated nodes should have is_obsolete set to True."""
    terms = hpo_loader.extract_hpo_terms(sample_data)

    obsolete_term = next(
        term for term in terms if term["hpo_id"] == "HP:0000057"
    )

    assert obsolete_term["is_obsolete"] is True


def test_duplicate_ids_are_removed(sample_data):
    """T6: Each HPO ID should appear only once."""
    terms = hpo_loader.extract_hpo_terms(sample_data)

    hpo_ids = [term["hpo_id"] for term in terms]

    assert hpo_ids.count("HP:0001250") == 1


def test_terms_are_sorted_by_hpo_id(sample_data):
    """T7: Extracted terms should be sorted by HPO ID."""
    terms = hpo_loader.extract_hpo_terms(sample_data)

    hpo_ids = [term["hpo_id"] for term in terms]

    assert hpo_ids == sorted(hpo_ids)


def test_download_failure_returns_error_without_traceback(
    monkeypatch, capsys
):
    """T8: A download failure should return 1 without a traceback."""

    def mock_failed_download(*args, **kwargs):
        raise requests.ConnectionError("Internet connection unavailable")

    monkeypatch.setattr(
        hpo_loader.requests,
        "get",
        mock_failed_download
    )

    result = hpo_loader.main([])

    captured = capsys.readouterr()

    assert result == 1
    assert "HPO download failed" in captured.err
    assert "Traceback" not in captured.err


def test_sqlite_loading_twice_does_not_create_duplicates(
    tmp_path, monkeypatch
):
    """T9: Running the SQLite loader twice should not duplicate rows."""
    monkeypatch.chdir(tmp_path)

    database_file = tmp_path / "hpo_test.db"

    arguments = [
        "--input",
        str(FIXTURE_PATH),
        "--sqlite",
        str(database_file)
    ]

    # First run
    assert hpo_loader.main(arguments) == 0

    # Second run with the same data
    assert hpo_loader.main(arguments) == 0

    with sqlite3.connect(database_file) as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM hpo_term")
        row_count = cursor.fetchone()[0]

    assert row_count == 3


def test_csv_is_created_with_expected_columns(tmp_path, monkeypatch):
    """Check that the CSV output has the required columns and rows."""
    monkeypatch.chdir(tmp_path)

    assert hpo_loader.main(["--input", str(FIXTURE_PATH)]) == 0

    with open("hpo_terms.csv", "r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        rows = list(reader)

    assert reader.fieldnames == ["hpo_id", "term_name", "is_obsolete"]
    assert len(rows) == 3