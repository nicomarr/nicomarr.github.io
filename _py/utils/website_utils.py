import os
import json
from typing import Tuple, Set, List, Dict, Any
from copy import deepcopy
from datetime import datetime
import pandas as pd
from openalex_api_lite import get_works

def update_citations(
    file_path: str,
    save_metadata_to_disk: bool = True,
    save_backup: bool = True,
    save_log_file: bool = True, 
    verbose: bool = True
) -> Tuple[bool, str]:
    """
    Update citation counts in articles metadata file using OpenAlex API data.

    Args:
        file_path (str): Path to the articles metadata CSV file.
        save_metadata_to_disk (bool): Whether to save the updated metadata to disk. Default is True. Set to False for testing on actual metadata.
        save_backup (bool): Whether to save a backup of the original metadata Default is True. Set to False for testing on actual metadata.
        save_log_file (bool): Whether to update the log file. Default is True. Set to False for testing on actual metadata.
        verbose (bool): Whether to show detailed progress messages. Default is True.

    Returns:
        Tuple[bool, str]: (success status, detailed message)
    """
    # Basic input validation
    file_path = os.path.expanduser(file_path) # Expand relative paths to absolute paths
    if not os.path.exists(file_path):
        return False, f"File not found: {file_path}"
    if not file_path.endswith('.csv'):
        return False, "Invalid file format. Must be CSV."
    assert isinstance(save_metadata_to_disk, bool), "save_to_disk must be a boolean."
    assert isinstance(save_backup, bool), "save_backup must be a boolean."
    assert isinstance(save_log_file, bool), "save_log_file must be a boolean."
    assert isinstance(verbose, bool), "verbose must be a boolean."

    # Read metadata file
    if verbose:
        print("Reading metadata file...")
    try:
        metadata = pd.read_csv(file_path, dtype=str)
        metadata["publication_date"] = pd.to_datetime(metadata["publication_date"])
        metadata = metadata.sort_values(by="publication_date", ascending=False)
        
        if metadata.empty:
            return False, "Empty metadata file"
        
        required_cols = ['oaid', 'cited_by_count', 'updated_date', 'doi_url']
        if not all(col in metadata.columns for col in required_cols):
            return False, f"Missing required columns: {set(required_cols) - set(metadata.columns)}"
            
        metadata_backup = deepcopy(metadata)
        
    except Exception as e:
        return False, f"Error reading metadata file: {str(e)}"

    # Fetch works data from OpenAlex API
    if verbose:
        print("Calling OpenAlex API ...")
    try:
        valid_ids = []
        for _, row in metadata.iterrows():
            oaid = str(row['oaid'])
            if pd.notna(oaid):
                oaid_clean = oaid.split('/')[-1] if '/' in oaid else oaid
                valid_ids.append(oaid_clean)

        if not valid_ids:
            return False, "No valid OpenAlex IDs found"

        works, failed_calls = get_works(
            ids=valid_ids,
            email=os.getenv("EMAIL"),
            select_fields="id,doi,cited_by_count,updated_date",
            show_progress=verbose
        )
    except Exception as e:
        return False, f"API error: {str(e)}"

    # Update citation counts
    updated_count = 0
    errors = []

    if verbose:
        print("Updating citation counts...")
    for idx, row in metadata.iterrows():
        try:
            oaid = str(row["oaid"])
            doi = row["doi_url"]
            current_citations = int(row["cited_by_count"]) if pd.notna(row["cited_by_count"]) else 0
            
            work = next((w for w in works if w["metadata"]["id"] == oaid), None)
            
            if not work:
                continue
                
            try:
                new_citations = work["metadata"]["cited_by_count"]
            except TypeError as e:
                if verbose:
                    print(f"TypeError: {e}")
                    print(f"Work: {work}")
                    print(f"Row type: {row['type']}")
                continue

            if new_citations > current_citations:
                if verbose:
                    print(f"Updating citations for OAID: {oaid} / DOI: {doi} from {current_citations} to {new_citations}")
                metadata.at[idx, 'cited_by_count'] = str(new_citations)
                metadata.at[idx, 'updated_date'] = work["metadata"]["updated_date"]
                updated_count += 1
            else:
                if verbose:
                    print(f"Citation count for OAID: {oaid} / DOI: {doi} is up-to-date. Citation count: {current_citations}. Skipping...")
                    
        except Exception as e:
            errors.append(f"Error processing {oaid}: {str(e)}")
            if verbose:
                print(f"Failed to update the cited_by_count for ID: {oaid}")
                print(e)
            continue

    # Save updates if any were made
    if updated_count > 0:
        if save_metadata_to_disk:
            if save_backup:
                try:
                    if verbose:
                        print("Saving a backup of the original metadata file...")
                    backup_timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
                    backup_path = file_path.replace(".csv", f"_bkp-{backup_timestamp}.csv")
                    metadata_backup.to_csv(backup_path, index=False)
                except Exception as e:
                    return False, f"Error saving backup: {str(e)}"

            if verbose:
                print("Saving updated metadata to disk...")
            try:
                metadata.to_csv(file_path, index=False)
            except Exception as e:
                return False, f"Error saving updated metadata to disk: {str(e)}"
            
            if save_log_file:
                if verbose:
                    print("Updating the log file...")
                try:
                    log_data = {
                        "last_modified": datetime.now().strftime('%Y-%m-%d'),
                        "status_message": f"Successfully updated citation counts for {updated_count} articles",
                    }
                    with open(os.path.join(os.path.dirname(file_path), "update-log.json"), 'w') as f:
                        json.dump(log_data, f, indent=2)
                except Exception as e:
                    return False, f"Error updating log file: {str(e)}"
        
            return True, f"Successfully updated citation counts for {updated_count} articles and saved metadata to disk."
        else: 
            return True, f"Successfully updated citation counts for {updated_count} articles. No changes saved to disk."
    else:
        return True, "No updates made. Citation counts were up-to-date."

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
