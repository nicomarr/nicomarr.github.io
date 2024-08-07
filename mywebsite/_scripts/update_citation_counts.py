#!/usr/bin/env python3
"""
update_citation_counts.py

This script updates the citation counts for all articles in the articles-metadata.csv file in the _data directory.
It only updates entries that have been modified in the OpenAlex database since the last modification date of the articles-metadata.csv file.

Usage: python update_citation_counts.py [--input INPUT_FILE] [--output OUTPUT_FILE] [--pmid_file PMID_FILE] [--verbose]

Dependencies: publications_page_utils.py, pandas, requests, tqdm

Version: 1.0.0
"""

import argparse
import logging
import os
import sys
from datetime import datetime, timedelta
from publications_page_utils import update_citation_counts

def main():
    parser = argparse.ArgumentParser(description="Update citation counts for publications.")
    parser.add_argument("--input", default="../_data/articles-metadata.csv", help="Path to input CSV file")
    parser.add_argument("--output", default="../_data/articles-metadata.csv", help="Path to output CSV file")
    parser.add_argument("--pmid_file", default="../_data/PMID-export.txt", help="Path to PMID file")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO if args.verbose else logging.WARNING)

    # Check if the articles-metadata.csv file was modified within the last 24 hours
    try:
        last_modified = datetime.fromtimestamp(os.path.getmtime(args.input))
        if (datetime.now() - last_modified) < timedelta(hours=24):
            logging.warning("The articles-metadata.csv file was modified within the last 24 hours. Aborting the update.")
            return 1
    except FileNotFoundError:
        logging.error(f"Input file not found: {args.input}")
        return 1

    # Import the PMIDs from a text file
    try:
        with open(args.pmid_file, "r") as file:
            pmids = file.read().splitlines()
    except FileNotFoundError:
        logging.error(f"PMID file not found: {args.pmid_file}")
        return 1

    # Get the email address from the environment variables
    email = os.environ.get("EMAIL", "")
    if not email:
        logging.warning("EMAIL environment variable not set. Proceeding without email.")

    try:
        update_citation_counts(
            pmids=pmids,
            email=email,
            file_path=args.input,
            verbose=args.verbose
        )
    except Exception as e:
        logging.error(f"Error updating citation counts: {e}")
        return 1

    logging.info("Citation counts updated successfully.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
