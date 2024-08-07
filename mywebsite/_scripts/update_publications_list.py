#!/usr/bin/env python3
"""
update_publications_list.py

This script updates the articles-metadata.csv file in the _data directory with new publications.
It only adds new articles and does not update or overwrite existing metadata.

Usage: python update_publications_list.py [--input INPUT_FILE] [--output OUTPUT_FILE] [--verbose]

Dependencies: publications_page_utils.py, pandas, requests

Version: 1.0.0
"""

import argparse
import logging
import os
import sys
from publications_page_utils import update_publications

def main():
    parser = argparse.ArgumentParser(description="Update publications list.")
    parser.add_argument("--input", default="../_data/PMID-export.txt", help="Path to input PMID file")
    parser.add_argument("--output", default="../_data/articles-metadata.csv", help="Path to output CSV file")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO if args.verbose else logging.WARNING)

    try:
        with open(args.input, "r") as file:
            pmids = file.read().splitlines()
    except FileNotFoundError:
        logging.error(f"Input file not found: {args.input}")
        return 1

    email = os.environ.get("EMAIL", "")
    if not email:
        logging.warning("EMAIL environment variable not set. Proceeding without email.")

    try:
        update_publications(
            pmids=pmids,
            email=email,
            file_path=args.output,
            verbose=args.verbose,
        )
    except Exception as e:
        logging.error(f"Error updating publications: {e}")
        return 1

    logging.info("Publications list updated successfully.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
