import argparse
import os
import sys
sys.path.append(os.path.expanduser("../utils"))
from website_utils import update_citations, append_metadata

def main():
    parser = argparse.ArgumentParser(description="Manage website metadata and citations.")
    
    # Main operation group
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--update-citations", action="store_true", help="Update citation counts in the metadata file")
    group.add_argument("--append-metadata", action="store_true", help="Append metadata for missing PMIDs")
    group.add_argument("--update-and-append", action="store_true", help="Perform both update and append operations")

    # Common arguments
    parser.add_argument("directory", type=str, help="Directory containing the metadata, log, and PMID files")
    parser.add_argument("--quiet", action="store_true", help="Run in quiet mode (no verbose output)")
    parser.add_argument("--include-errata", action="store_true", help="Include errata in the appended metadata")

    args = parser.parse_args()

    # Define file paths
    metadata_file = os.path.join(args.directory, "articles-metadata.csv")
    log_file = os.path.join(args.directory, "update-log.json")
    pmid_file = os.path.join(args.directory, "PMID-export.txt")

    # Validate file existence
    if not os.path.exists(metadata_file):
        parser.error(f"Metadata file not found: {metadata_file}")
    if not os.path.exists(log_file):
        parser.error(f"Log file not found: {log_file}")
    if (args.append_metadata or args.update_and_append) and not os.path.exists(pmid_file):
        parser.error(f"PMID file not found: {pmid_file}")

    success_messages = []
    error_messages = []

    if args.update_citations or args.update_and_append:
        success, message = update_citations(metadata_file, verbose=not args.quiet)
        if success:
            success_messages.append(f"Update citations operation: {message}")
        else:
            error_messages.append(f"Update citations operation completed without saving new data: {message}")

    if args.append_metadata or args.update_and_append:
        success, message = append_metadata(metadata_file, pmid_file, 
                                           exclude_errata=not args.include_errata, 
                                           verbose=not args.quiet)
        if success:
            success_messages.append(f"Append metadata operation: {message}")
        else:
            error_messages.append(f"Append metadata operation completed without saving new data: {message}")

    # Print results
    for message in success_messages:
        print(message)
    for message in error_messages:
        print(message)

    # Exit with error if any operation failed
    if error_messages:
        exit(1)

if __name__ == "__main__":
    main()

