import argparse
import csv
import json
import sqlite3
import sys
import time
from pathlib import Path

import requests


HPO_URL = "https://purl.obolibrary.org/obo/hp.json"

CSV_COLUMNS = ["hpo_id", "term_name", "is_obsolete"]


def download_hpo_json():
    """Download the official HPO JSON file and return its contents."""
    response = requests.get(HPO_URL, timeout=60)
    response.raise_for_status()
    return response.json()


def read_json_file(file_path):
    """Read HPO JSON data from a local file."""
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def extract_hpo_terms(data):
    """Extract, clean, deduplicate, and sort valid HPO terms."""
    nodes = data["graphs"][0]["nodes"]

    terms_by_id = {}

    for node in nodes:
        node_id = node.get("id", "")
        term_name = node.get("lbl")

        # Keep only CLASS nodes with an HPO identifier.
        if node.get("type") != "CLASS":
            continue

        if "HP_" not in node_id:
            continue

        # Skip nodes without a term name.
        if not term_name:
            continue

        # Convert HP_0001250 into HP:0001250.
        hpo_id = "HP:" + node_id.rsplit("HP_", 1)[1]

        # Check whether the term is deprecated.
        meta = node.get("meta") or {}
        is_obsolete = meta.get("deprecated") is True

        # Using the ID as a dictionary key removes duplicates.
        # If an ID appears again, the latest occurrence replaces it.
        terms_by_id[hpo_id] = {
            "hpo_id": hpo_id,
            "term_name": term_name,
            "is_obsolete": is_obsolete,
        }

    # Sort by HPO ID.
    return sorted(
        terms_by_id.values(),
        key=lambda term: term["hpo_id"]
    )


def write_csv(terms, output_file="hpo_terms.csv"):
    """Write extracted HPO terms into a CSV file."""
    with open(output_file, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=CSV_COLUMNS)
        writer.writeheader()

        for term in terms:
            row = term.copy()
            row["is_obsolete"] = str(row["is_obsolete"]).lower()
            writer.writerow(row)


def load_sqlite(terms, database_file):
    """Insert or replace HPO terms in an SQLite database."""
    with sqlite3.connect(database_file) as connection:
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS hpo_term (
                hpo_id TEXT PRIMARY KEY,
                term_name TEXT NOT NULL,
                is_obsolete INTEGER NOT NULL
            )
        """)

        cursor.executemany("""
            INSERT OR REPLACE INTO hpo_term
            (hpo_id, term_name, is_obsolete)
            VALUES (?, ?, ?)
        """, [
            (
                term["hpo_id"],
                term["term_name"],
                int(term["is_obsolete"])
            )
            for term in terms
        ])


def main(argv=None):
    """Run the HPO loader from the command line."""
    parser = argparse.ArgumentParser(
        description="Download and process Human Phenotype Ontology terms."
    )

    parser.add_argument(
        "--input",
        help="Path to a local HPO JSON file instead of downloading."
    )

    parser.add_argument(
        "--sqlite",
        help="Optional SQLite database file to store HPO terms."
    )

    args = parser.parse_args(argv)

    start_time = time.perf_counter()

    try:
        if args.input:
            data = read_json_file(args.input)
        else:
            data = download_hpo_json()

    except requests.RequestException as error:
        print(f"Error: HPO download failed: {error}", file=sys.stderr)
        return 1

    except (OSError, json.JSONDecodeError) as error:
        print(f"Error: Could not read HPO JSON: {error}", file=sys.stderr)
        return 1

    try:
        terms = extract_hpo_terms(data)

        write_csv(terms)

        if args.sqlite:
            load_sqlite(terms, args.sqlite)

    except (KeyError, IndexError, TypeError, sqlite3.Error, OSError) as error:
        print(f"Error: Could not process HPO data: {error}", file=sys.stderr)
        return 1

    total_terms = len(terms)
    obsolete_count = sum(term["is_obsolete"] for term in terms)
    elapsed_time = time.perf_counter() - start_time

    print("HPO loading completed successfully!")
    print(f"Total terms: {total_terms}")
    print(f"Obsolete terms: {obsolete_count}")
    print(f"Time taken: {elapsed_time:.2f} seconds")

    return 0


if __name__ == "__main__":
    sys.exit(main())