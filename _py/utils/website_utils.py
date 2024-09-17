import os
from typing import Tuple, Set, List, Dict, Any
from copy import deepcopy
from datetime import datetime
import pandas as pd
from openalex_api_utils import get_works
import json

def update_citations(file_path: str, verbose: bool = True) -> Tuple[bool, str]:
    """
    Update the citation counts in the articles metadata file.

    Args:
        file_path (str): Path to the articles metadata file.
        verbose (bool): Whether to show verbose messages during the process, including progress and errors.

    Returns:
        tuple: A tuple containing a boolean indicating if any updates were made, and a message string with details.
    """

    # Input validation
    assert file_path.endswith(".csv"), "Invalid file format. Please provide a CSV file."
    assert isinstance(verbose, bool), "Verbose must be a boolean."
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return False, f"File not found: {file_path}"

    # Read the metadata file and sort by publication date, descending
    if verbose: print("Reading the metadata file...")
    try:
        metadata = pd.read_csv(file_path, dtype=str)
        metadata_bkp = deepcopy(metadata) # Make a deepcopy of the DataFrame to save a backup
        metadata['publication_date'] = pd.to_datetime(metadata['publication_date'], format='%Y-%m-%d', errors='coerce') # The errors='coerce' parameter will replace any unparsable dates with NaT (Not a Time) values
        if metadata['publication_date'].isna().any(): # Check if there are any NaT values
            if verbose:
                print("Warning: Some publication dates could not be parsed. These will be excluded from sorting.")
                entries_with_missing_dates = metadata[metadata['publication_date'].isna()]
                print(
                    f"Entries with publication dates that could not be parsed: idx {entries_with_missing_dates.index.tolist()}, "
                    f"PMIDs {entries_with_missing_dates['pmid'].tolist()}, "
                    f"Article titles {entries_with_missing_dates['article_title'].tolist()}"
                    )
            metadata = metadata.dropna(subset=['publication_date']) # Drop rows with missing publication dates
        metadata = metadata.sort_values(by="publication_date", ascending=False)
        metadata.reset_index(drop=True, inplace=True)
    except Exception as e:
        if verbose:
            print(f"An error occurred while reading the metadata file: {e}")
        return False, f"An error occurred while reading the metadata file: {e}"
    
    # Extract PMIDs from the metadata
    if verbose: print("Extracting PMIDs from the metadata...")
    try:
        pmids = metadata["pmid"].astype(str).tolist()
    except Exception as e:
        if verbose:
            print(f"An error occurred while extracting PMIDs from the metadata: {e}")
        return False, f"An error occurred while extracting PMIDs from the metadata: {e}"
    
    # Make API calls to get the works for the PMIDs
    if verbose: print("Fetching works data from the API...")
    works, failed_calls = get_works(
        ids=pmids,
        email=os.environ.get("EMAIL"), # Will return an empty string if the variable is not set
        select_fields="id,doi,title,cited_by_count,updated_date",
        show_progress=verbose
    )
    
    # Iterate over the rows in metadata and update the cited_by_count and updated_date
    if verbose: print("Updating the citation counts...")
    counter = 0
    for index, row in metadata.iterrows():
        id = row["oaid"]
        doi = row["doi_url"]
        updated_date = row["updated_date"]
        current_cited_by_count = row["cited_by_count"]
        work = next((work for work in works if work["metadata"]["id"] == id), None)
        new_cited_by_count = work["metadata"]["cited_by_count"]
        if new_cited_by_count > int(current_cited_by_count):
            try:
                if verbose: print(f"Updating the cited_by_count for ID: {id} / DOI: {doi} from {current_cited_by_count} to {new_cited_by_count}")
                metadata.at[index, "cited_by_count"] = new_cited_by_count
                metadata.at[index, "updated_date"] = work["metadata"]["updated_date"] # Leave the date as a string
                counter += 1
            except Exception as e:
                if verbose: print(f"Failed to update the cited_by_count for PMID: {pmid}. Error: {e}")
        else:
            if verbose: print(f"Citation count {current_cited_by_count} for ID {id} with DOI {doi} is up-to-date. Skipping...")
            continue

    if verbose: print(f"Updated values for {counter} articles.")
    if counter > 0:
        if verbose: print("Saving the updated metadata to a CSV file...")
        metadata.to_csv(file_path, index=False)
        if verbose: print("Saving a backup file to disk...")
        bkp_file_path = file_path.replace(".csv", f"_bkp-{datetime.now().strftime('%Y%m%d-%Hh%Mm')}.csv")
        metadata_bkp.to_csv(bkp_file_path, index=False)
        if verbose: print("Metadata updated successfully.")

        # Get the path to the log file from the metadata file path
        log_file_path = os.path.join(os.path.dirname(file_path), "update-log.json") 
        
        # Update the log file
        try:
            if verbose: print("Updating the log file...")
            with open(log_file_path, "r") as f:
                update_log = json.load(f)
            current_date = datetime.now().strftime("%Y-%m-%d")
            update_log["last_modified"] = current_date # Expected format: {"last_modified": "2024-08-06"}
            with open(log_file_path, "w") as f:
                json.dump(update_log, f)
            if verbose: print(f"Log file updated successfully.")
        except Exception as e:
            if verbose: print(f"Error updating log file: {e}. Creating a new log file...")
            current_date = datetime.now().strftime("%Y-%m-%d")
            with open(log_file_path, "w") as f:
                json.dump({"last_modified": current_date}, f)
            if verbose: print(f"New log file created successfully.")

        return True, f"Updated values for {counter} articles and saved file to {file_path}. Backup saved as {bkp_file_path}"
    else:
        return False, "Loaded metadata were up-to-date. No changes were made."

from typing import List, Dict, Any

def parse_data(works: List[Dict[str, Any]], exclude_errata: bool = True) -> pd.DataFrame:
    """
    Parse the raw data from the OpenAlex API and create a DataFrame.

    This function extracts relevant information from each work in the input list
    and creates a DataFrame with specified columns. It also removes duplicates
    based on PMID and filters out errata (if specified).

    Args:
        works (List[Dict[str, Any]]): A list of dictionaries, where each dictionary
            contains metadata about a work.
        exclude_errata (bool): Whether to exclude errata from the DataFrame.

    Returns:
        pd.DataFrame: A DataFrame containing extracted and processed information
        from the works.

    Example:
        >>> df_works = parse_data(works)
        >>> df_works.head()

    Note:
        The function extracts the following information for each work:
        - First author's last name
        - Article title
        - Journal name
        - Publication year and date
        - PMID, PMCID, and OpenAlex ID
        - PDF URL (if available)
        - DOI URL
        - Citation count and URL
        - Work type and Crossref type
        - Updated date (from the API)
    """

    # Initialize an empty list to store the extracted data, and iterate over the works data to extract relevant information
    oa_data = []
    for work in works:
        metadata = work["metadata"]
        first_author_last_name = metadata["authorships"][0]["author"]["display_name"].split(" ")[-1]
        article_title = metadata["title"]
        journal = metadata["primary_location"]["source"]["display_name"]
        publication_year = str(metadata["publication_year"])
        publication_date = metadata["publication_date"]
        if publication_date:
            try:
                publication_date = pd.to_datetime(publication_date).strftime('%Y-%m-%d')
            except ValueError:
                pass # If the date can't be parsed, keep the original string
        pmid = metadata["ids"].get("pmid", "").split("/")[-1] # To remove the url prefix
        pmcid = metadata["ids"].get("pmcid")
        if pmcid is not None:
            pmcid = pmcid.split("/")[-1] # To remove the url prefix
        else: 
            pmcid = "" # To replace None with an empty string
        oaid = metadata["id"]
        try:
            pdf_url = metadata.get("best_oa_location", {}).get("pdf_url", "not available")
        except AttributeError:
            pdf_url = "not available"
        if pdf_url is None:
            pdf_url = "not available"
        doi_url = metadata["doi"]
        cited_by_count = str(metadata["cited_by_count"])
        cited_by_ui_url = metadata["cited_by_api_url"].replace("api.openalex.org", "openalex.org")
        work_type = metadata.get("type")
        type_crossref = metadata.get("type_crossref")
        updated_date = metadata.get("updated_date")

        oa_data.append([
            first_author_last_name, article_title, journal, publication_year,
            publication_date, pmid, pmcid, oaid, pdf_url, doi_url,
            cited_by_count, cited_by_ui_url, work_type, type_crossref, updated_date
        ])

    columns = [
        'first_author_last_name', 'article_title', 'journal',
        'publication_year', 'publication_date', 'pmid', 'pmcid', 'oaid',
        'pdf_url', 'doi_url', 'cited_by_count', 'cited_by_ui_url', 'type',
        'type_crossref', 'updated_date'
    ]

    # Create a DataFrame with the specified columns
    df_works = pd.DataFrame(oa_data, columns=columns, dtype=str)
    df_works = df_works.drop_duplicates(subset=["pmid"])
    if exclude_errata:
        df_works = df_works[df_works["type"] != "erratum"]

    # Parse the publication date as a datetime object with the format 'YYYY-MM-DD'
    df_works["publication_date"] = pd.to_datetime(df_works["publication_date"], errors='coerce').dt.strftime('%Y-%m-%d')
    
    # Sort the DataFrame by publication date in descending order
    df_works = df_works.sort_values(by="publication_date", ascending=False)
    df_works.reset_index(drop=True, inplace=True)

    return df_works

import os
import pandas as pd
from datetime import datetime
import argparse
from copy import deepcopy

def append_metadata(metadata_file_path: str, pmid_file_path: str, exclude_errata: bool = True, verbose: bool = True) -> Tuple[bool, str]:
    """
    Append metadata for missing PMIDs to an existing metadata file.

    Args:
        metadata_file_path (str): Path to CSV file containing existing metadata.
        pmid_file_path (str): Path to file containing list of PMIDs.
        exclude_errata (bool): Whether to exclude errata from the metadata.
        verbose (bool): Whether to show verbose messages during the process.

    Returns:
        tuple: A tuple containing a boolean indicating if any updates were made, and a message string with details.
    """

    # Input validation
    assert metadata_file_path.endswith(".csv"), "Invalid file format. Please provide a CSV file."
    assert os.path.exists(metadata_file_path), "Metadata file not found."
    assert pmid_file_path.endswith(".txt"), "Invalid file format. Please provide a TXT file."
    assert os.path.exists(pmid_file_path), "PMID file not found."
    assert isinstance(verbose, bool), "Verbose must be a boolean."

    # Read existing metadata
    if verbose: print("Reading the existing metadata file...")
    try:
        metadata = pd.read_csv(metadata_file_path, dtype=str)
        metadata_bkp = deepcopy(metadata) # Make a deepcopy of the DataFrame to save a backup
    except Exception as e:
        if verbose:
            print(f"An error occurred while reading the metadata file: {e}")
        return False, f"An error occurred while reading the metadata file: {e}"

    # Read PMIDs from file
    if verbose: print("Reading the PMID file...")
    try:
        with open(pmid_file_path, 'r') as f:
            pmids = set(line.strip() for line in f)
    except Exception as e:
        if verbose:
            print(f"An error occurred while reading the PMID file: {e}")
        return False, f"An error occurred while reading the PMID file: {e}"

    # Find missing PMIDs
    if verbose: print("Searching for new PMIDs not in the metadata...")
    existing_pmids: Set[str] = set(metadata["pmid"])
    new_pmids: Set[str] = pmids - existing_pmids
    new_pmids_str = ", ".join(new_pmids) # Convert to a string with comma-separated values
    if verbose: print(f"Found {len(new_pmids)} new PMID(s): {new_pmids_str}.")
    if len(new_pmids) == 0:
        return False, "No new PMIDs found."
    else:
        try:
            # Make API calls to get the missing PMIDs
            select_fields: str = (
                "id,title,doi,primary_location,authorships,publication_year,"
                "publication_date,ids,best_oa_location,cited_by_count,"
                "cited_by_api_url,type,type_crossref,updated_date"
            )
            new_articles, failed_calls = get_works(
                ids=list(new_pmids),
                email=os.environ.get("EMAIL"),
                select_fields=select_fields,
                show_progress=verbose
            )
            if verbose: print(f"API calls completed. Failed calls: {len(failed_calls)}")
        except Exception as e:
            if verbose:
                print(f"An error occurred while fetching works data from the API: {e}")
            return False, f"An error occurred while fetching works data from the API: {e}"

        # Parse the data for new articles
        if verbose: print("Parsing the data for new articles...")
        try:
            df_new_articles = parse_data(new_articles, exclude_errata=exclude_errata)
        except Exception as e:
            if verbose:
                print(f"An error occurred while parsing the data for new articles: {e}")
            return False, f"An error occurred while parsing the data for new articles: {e}"
        
        if df_new_articles.empty:
            if exclude_errata:
                if verbose: print("No new articles found (Errata excluded).")
                return False, "No new articles found (Errata excluded)."
            else:
                if verbose: print("No new articles found.")
                return False, "No new articles found."
        else:
            # Append the new articles to the existing metadata
            new_pmids = set(df_new_articles["pmid"])
            new_pmids = ", ".join(new_pmids) # Convert to a string with comma-separated values
            if verbose: print(f"Appending {len(df_new_articles)} new article(s) with PMID(s) {new_pmids} to the existing metadata...")
            try:
                metadata = pd.concat([df_new_articles, metadata], ignore_index=True)
            except Exception as e:
                if verbose:
                    print(f"An error occurred while appending the new articles to the existing metadata: {e}")
                return False, f"An error occurred while appending the new articles to the existing metadata: {e}"

            # Save the updated metadata to a CSV file
            if verbose: print("Saving the updated metadata to a CSV file...")
            metadata.to_csv(metadata_file_path, index=False)
            if verbose: print("Saving a backup file to disk...")
            bkp_file_path = metadata_file_path.replace(".csv", f"_bkp-{datetime.now().strftime('%Y%m%d-%Hh%Mm')}.csv")
            metadata_bkp.to_csv(bkp_file_path, index=False)
            if verbose: print("Metadata updated successfully.")

            # Get the path to the log file from the metadata file path
            log_file_path = os.path.join(os.path.dirname(metadata_file_path), "update-log.json")
            
            # Update the log file
            try:
                if verbose: print("Updating the log file...")
                with open(log_file_path, "r") as f:
                    update_log = json.load(f)
                current_date = datetime.now().strftime("%Y-%m-%d")    
                update_log["last_modified"] = current_date # Expected format: {"last_modified": "2024-08-06"}
                with open(log_file_path, "w") as f:
                    json.dump(update_log, f)
                if verbose: print(f"Log file updated successfully.")
            except Exception as e:
                if verbose: print(f"Error updating log file: {e}. Creating a new log file...")
                current_date = datetime.now().strftime("%Y-%m-%d")
                with open(log_file_path, "w") as f:
                    json.dump({"last_modified": current_date}, f)
                if verbose: print(f"New log file created successfully.")

            return True, f"Appended {len(df_new_articles)} article(s) and saved file to {metadata_file_path}. Backup saved as {bkp_file_path}"
