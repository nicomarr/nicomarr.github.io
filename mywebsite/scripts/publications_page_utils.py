########################################################################################
# Utility functions for working with the OpenAlex API.
# These functions help automatically generate and update the articles-metadata.csv and 
# update-log.json files in the _data directory, which are needed to serve the publications page.
# This file is built from contents in notebook `generate_and_update_publications_data.ipynb`.
# Version: 1.0.0
# Dependencies: requests, pandas, json, os, datetime, time, tqdm, typing, IPython.display
########################################################################################

import os
import requests
import json

def search_works_by_author(author_id: str, email: str, verbose: bool=False) -> dict:
    """
    Search for works by author ID using the OpenAlex API.

    Args:
        author_id (str): Identifier of the author to search for.
        email (str): The email address to use for the query. Optional.
        verbose (bool): Whether to print out additional information. Default is False.

    Returns:
        dict: The search results from the OpenAlex database.
    """
    # Validate inputs
    if not author_id:
        raise ValueError("Author ID is required.")
    if not author_id.startswith("a"):
        raise ValueError("Author ID must start with 'a'.")

    # If no email is provided, use an empty string
    if not email:
        email = ""

    # Set the base URL and the API endpoint
    base_url = "https://api.openalex.org/"
    url = f"{base_url}works?"

    params = {
        "mailto": email,
        "filter": f"authorships.author.id:{author_id}",
        "per-page": 200,
        "select": "id,ids,doi,title,display_name,authorships,best_oa_location,primary_location,locations,publication_year,publication_date,biblio,open_access,topics,concepts,cited_by_count,cited_by_api_url,type,type_crossref,updated_date",
    }
    # filter options: abstract.search, display_name.search, fulltext.search, raw_affiliation_strings.search, title.search, title_and_abstract.search
    # select option: id, doi, title, authorships, publication_year, publication_date, ids, language, primary_location, type, type_crossref, open_access, has_fulltext, cited_by_count, cited_by_percentile_year, biblio, primary_topic, topics, keywords, concepts, mesh, best_oa_location, sustainable_development_goals, referenced_works, related_works, ngrams_url, cited_by_api_url, counts_by_year, updated_date, created_date

    # Initialize cursor
    cursor = "*"

    # Initialize the list to store all results and the number of API queries
    api_query_count = 0
    search_results = []

    # Loop through pages
    while cursor:
        params["cursor"] = cursor
        response = requests.get(url, params=params)
        if response.status_code != 200:
            print("Error:", response.json())
            break
        current_page_results = response.json()["results"]
        for result in current_page_results:
            # Store these results in the list we created before the loop we are currently in
            search_results.append(result)
        api_query_count += 1

        # Update cursor using the `next_cursor` metadata field in the response
        cursor = response.json()["meta"]["next_cursor"]
    if verbose:
        print(f"Done paging through results. Made {api_query_count} API queries, retrieved {len(search_results)} results.")
    
    return search_results

# Example usage:
# search_results = search_works_by_author(author_id, email)
########################################################################################


import time
import requests
from datetime import datetime, timedelta
from tqdm import tqdm

def search_works_by_pmid(pmids: list, email: str, show_progress: bool = False, verbose: bool = False) -> list:
    """
    Get information about works from OpenAlex API. Works are scholarly documents like journal articles, books, datasets, and theses.
    
    Args:
        pmids (list): List of PubMed IDs of works to get information about.
        email (str): Email address to use in the API request. Optional but recommended.
        show_progress (bool, optional): If True, displays a progress bar. Defaults to False.
        verbose (bool, optional): If True, prints detailed status messages. Defaults to False. Disabled if show_progress is True.
        
    Returns:
        list: List of dictionaries containing information about the works.
    """

    # Input validation
    assert isinstance(pmids, list), "PMIDs must be provided as a list."
    assert isinstance(verbose, bool), "Verbose must be a boolean value."

    # Remove any duplicates from the list of PMIDs
    pmids = list(set([pmid for pmid in pmids if pmid]))

    # Remove any spaces from each item in the list of PMIDs
    pmids = [pmid.strip() for pmid in pmids]

    # If no email is provided, use an empty string
    if not email:
        email = ""
    
    # Initialize variables used for the API request and function
    base_url = "https://api.openalex.org/works/"
    params = {
        "mailto": email,
        "select": "id,ids,doi,title,display_name,authorships,best_oa_location,primary_location,locations,publication_year,publication_date,biblio,open_access,topics,concepts,cited_by_count,cited_by_api_url,type,type_crossref,updated_date",
    }

    # Initializer variables
    search_results = []
    iter_count = 0
    now = datetime.now()  # Initialize 'now' variable

    # Display a progress bar if show_progress is True
    if show_progress:
        iterable = tqdm(pmids, desc="Retrieving works")
        verbose = False  # Disable verbose mode if show_progress is True.
    else:
        iterable = pmids

    # Iterate over each PMID in the list to retrieve information about the works.
    for pmid in iterable:
        # Initialize variables used for each iteration
        response = None
        data = None
        url = None
        
        if verbose:
            print("---")

        # Handle API rate limit
        if iter_count > 9:
            time_delta = datetime.now() - now
            if time_delta < timedelta(seconds=1):
                remaining_time = 1 - time_delta.total_seconds()
                if verbose:
                    print(f"Number of requests reached 10. Sleeping for {round(remaining_time, 3)} seconds...")
                time.sleep(remaining_time)
                iter_count = 0
                now = datetime.now()

        # Construct the URL for the API call
        url = f"{base_url}pmid:{pmid}"

        # Retrieve data for the work using the OpenAlex API
        try: 
            response = requests.get(url, params=params)    
        except requests.RequestException as e:
            if verbose:
                print(f"An error occurred while making an API call with PMID {pmid}: {e}")
            continue

        # Handle unsuccessful API calls    
        if response.status_code != 200: 
            if verbose:
                print(f"API call for work with PMID {pmid} was not successful. Status code: {response.status_code}")
            continue

        # Continue if the API call was successful   
        else:    
            data = response.json()
            if verbose:
                print(f"Successfully retrieved metadata for work with PMID {pmid}.")

        search_results.append(data)
        iter_count += 1  # Increment the iteration count
            
    return search_results

# Example usage:
# search_results = search_works_by_pmid(pmids, email, show_progress=True)
########################################################################################


from IPython.display import display, HTML
from typing import List, Dict, Any

def process_raw_search_results(search_results: List[Dict[str, Any]], display_html: bool = False) -> List[Dict[str, Any]]:
    """
    Format the search results retrieved from the OpenAlex API.

    Args:
        search_results (dict): List of dictionaries containing information about the works.
        display_html (bool): Boolean flag to control HTML display. Defaults to False.

    Returns:
        List of processed article information.
    """
    articles = []

    for work in search_results:
        first_author_last_name = work["authorships"][0]["author"]["display_name"].split(" ")[-1]
        title = str(work["title"])
        title = title.replace('"', '')
        publication_year = work["publication_year"]
        publication_date = work["publication_date"]

        # Get the journal name
        journal = "Unknown"  # Default value
        primary_location = work.get("primary_location")
        if primary_location is not None:
            source = primary_location.get("source")
            if source is not None:
                journal = source.get("display_name", "Unknown")

        # Get the number of citations and the URL to view the citing articles
        cited_by_api_url = work["cited_by_api_url"]
        cited_by_ui_url = cited_by_api_url.replace("api.openalex.org", "openalex.org")
        cited_by_count = work["cited_by_count"]

        # Get DOI URL
        doi = work.get("doi")
        doi_url = doi if doi and doi.startswith("http") else "not available"

        # Initialize pdf_url
        _pdf_url = None
        pdf_url = "not available"

        # Get the PMID
        pmid = work["ids"].get("pmid", "")
        if pmid.startswith("http"):
            pmid = pmid.split("/")[-1]

        # Get OpenAlex ID
        oaid = work["id"]

        # Get the PMCID and construct pdf_url
        pmcid = work["ids"].get("pmcid", "")
        if pmcid.startswith("http"):
            pmcid = pmcid.split("/")[-1]
            pdf_url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmcid}/pdf/"
        elif pmcid.startswith("PMC"):
            pdf_url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmcid}/pdf"

        # Update the PDF URL from the best OA location
        best_oa_location = work.get("best_oa_location")
        if best_oa_location is not None:
            _pdf_url = best_oa_location.get("pdf_url", None)
            if _pdf_url is not None and _pdf_url.startswith("http"):
                pdf_url = _pdf_url

        if display_html:
            print(pmid, pmcid, oaid)
            display(
                HTML(f"{first_author_last_name} <i>et al.</i> <b>{title}.</b> {journal} {publication_year}"),
                HTML(f"""
                {"<a href='" + doi_url + "' target='_blank'>Read article</a>" if doi_url != "not available" else "DOI not available"}
                | 
                {"<a href='" + pdf_url + "' target='_blank'>Download PDF</a>" if pdf_url != "not available" else "PDF not available"}
                | 
                <a href='{cited_by_ui_url}'>Cited by</a>: {cited_by_count}
                """.replace('\n', ' ')),
                HTML("<hr>")
            )

        article = {
            "first_author_last_name": first_author_last_name,
            "article_title": title,
            "journal": str(journal),
            "publication_year": publication_year,
            "publication_date": publication_date,
            "pmid": str(pmid),
            "pmcid": str(pmcid),
            "oaid": str(oaid),
            "pdf_url": str(pdf_url),
            "doi_url": str(doi_url),
            "cited_by_count": cited_by_count,
            "cited_by_ui_url": str(cited_by_ui_url),
            "type": work["type"],
            "type_crossref": work["type_crossref"],
            "updated_date": work["updated_date"],
        }
        articles.append(article)

    return articles

# Example usage:
# processed_search_results = process_raw_search_results(search_results)
########################################################################################


import pandas as pd
from typing import List, Dict, Any

def save_results_to_csv(
    articles: List[Dict[str, Any]], 
    output_path: str = "../_data/articles-metadata.csv", 
    exclude: List[str] = [], 
    is_journal_article: bool = True, 
    has_doi: bool = True, 
    has_pmid: bool = True, 
    sort_by_publication_date: bool = True, 
    verbose: bool = False,
    return_df: bool = False,
) -> None:
    """
    Save the processed search results to a CSV file.

    Args:
        articles (list): List of processed article information.
        output_path (str): Path to save the CSV file. Defaults to "../_data/articles-metadata.csv".
        exclude (list): List of article IDs to exclude from the CSV file. Defaults to an empty list. Accepts OpenAlex IDs or PMIDs.
        is_journal_article (bool): Whether to include only journal articles. Defaults to True.
        has_doi (bool): Whether to include only articles with DOIs. Defaults to True.
        has_pmid (bool): Whether to include only articles with PMIDs. Defaults to True.
        sort_by_publication_date (bool): Whether to sort the articles by publication date. Defaults to True.
        verbose (bool): Whether to print out additional information. Defaults to False.

    Returns:
        None
    """
    # Create a DataFrame from the list of articles
    df = pd.DataFrame(articles)

    # Drop duplicates
    df.drop_duplicates(keep=False, inplace=True)

    # Filter the DataFrame based on flags
    if is_journal_article:
        df = df[df["type_crossref"] == "journal-article"]
        df = df[~df["type"].isin(["erratum", "dataset"])]

    if has_doi:
        df = df[~df["doi_url"].isnull() & (df["doi_url"] != "")]

    if has_pmid:
        df = df[~df["pmid"].isnull() & (df["pmid"] != "")]

    # Remove works that are in the exclude list
    df = df[~df["pmid"].isin(exclude) & ~df["oaid"].isin(exclude)]

    # Sort the DataFrame by publication date
    if sort_by_publication_date:
        # Publication date is in the format "YYYY-MM-DD"; may need to convert to datetime for proper sorting
        df.sort_values("publication_date", ascending=False, inplace=True)

    # Reset the index of the DataFrame
    df.reset_index(drop=True, inplace=True)

    # Check if DataFrame is empty before saving
    if df.empty:
        print("No articles to save after filtering.")
        return

    # Save the DataFrame to a CSV file
    df.to_csv(output_path, index=False)
    
    # Save a json log file with a datetime timestamp of the metadata file to reflect the last update date on the bottom of the publications page
    update_log(output_path) 

    if verbose:
        print(f"Saved data for {len(df)} articles to {output_path}")

    if return_df:
        return df

# Example usage:
# save_results_to_csv(processed_search_results, output_path="../_data/articles-metadata.csv", verbose=True)
########################################################################################


def update_publications(
    pmids: list,
    email: str,
    file_path: str = "../_data/articles-metadata.csv",
    exclude: List[str] = [], 
    is_journal_article: bool = True, 
    has_doi: bool = True, 
    has_pmid: bool = True, 
    sort_by_publication_date: bool = True,
    verbose: bool = False,
    ) -> None:
    """
    Updates the publications by fetching new articles based on provided PMIDs.

    Args:
        pmids (list): List of PMIDs to check for new articles.
        email (str): Email address for API requests.
        file_path (str): Path to the CSV file containing existing articles.
        exclude (List[str]): List of PMIDs or OAIDs to exclude from the results.
        is_journal_article (bool): Flag to filter for journal articles.
        has_doi (bool): Flag to filter for articles with a DOI.
        has_pmid (bool): Flag to filter for articles with a PMID.
        sort_by_publication_date (bool): Flag to sort the results by publication date.
        verbose (bool): Flag to print additional information.

    Returns:
        None
    """
    # Load the existing data
    df = pd.read_csv(file_path)

    # Determine which PMIDs are in the pmids list but not in the dataframe.pmid column
    new_pmids = set(pmids) - set(df["pmid"].astype(str))

    # Call OpenAlex API to retrieve information about the new works
    new_results = search_works_by_pmid(list(new_pmids), email, show_progress=True)

    # Format the new results
    new_results_formatted = process_raw_search_results(new_results, display_html=False)

    # Cast the new results to a DataFrame
    df_new = pd.DataFrame(new_results_formatted)

    # Filter the DataFrame with the new results based on flags
    if is_journal_article:
        df_new = df_new[df_new["type_crossref"] == "journal-article"]
        df_new = df_new[~df_new["type"].isin(["erratum", "dataset"])]

    if has_doi:
        df_new = df_new[~(df_new["doi_url"].isnull() | (df_new["doi_url"] == ""))]

    if has_pmid:
        df_new = df_new[~(df_new["pmid"].isnull() | (df_new["pmid"] == ""))]

    # Remove works that are in the exclude list
    df_new = df_new[~df_new["pmid"].isin(exclude) & ~df_new["oaid"].isin(exclude)]

    # Check if the new DataFrame is empty
    if df_new.empty:
        if verbose:
            print("No new articles to add.")
        return

    # Append the new results to the existing DataFrame
    df = pd.concat([df, df_new], ignore_index=True)

    # Sort the DataFrame by publication date
    if sort_by_publication_date:
        df.sort_values("publication_date", ascending=False, inplace=True)

    # Reset the index of the DataFrame
    df.reset_index(drop=True, inplace=True)

    # Save the updated DataFrame to the CSV file
    df.to_csv(file_path, index=False)
    
    # Update the json log file with a datetime timestamp of the metadata file to reflect the last update date on the bottom of the publications page
    update_log(file_path) 

    if verbose:
        print(f"Updated the data with {len(df_new)} new article(s).")

# Example usage:
# update_publications(
#     pmids=list(pmids),
#     email=EMAIL,
#     file_path="../_data/articles-metadata.csv",
#     verbose=True,
# )
########################################################################################


import os
import time
import requests
import pandas as pd
from datetime import datetime, timedelta

def update_citation_counts(pmids: list, email: str, file_path: str = "../_data/articles-metadata.csv", verbose: bool = False) -> None:
    """
    Update the citation counts for the articles in the CSV file.

    Args:
        pmids (list): List of PMIDs to update the citation counts for.
        email (str): Email address to use in the API request. Optional but recommended.
        file_path (str): Path to the CSV file containing the articles metadata. Defaults to "../_data/articles-metadata.csv".
        verbose (bool): Whether to print out additional information. Defaults to False.
    """

    # Input validation
    assert isinstance(pmids, list), "PMIDs must be provided as a list."
    assert isinstance(verbose, bool), "Verbose must be a boolean value."

    # If no email is provided, use an empty string
    if not email:
        email = ""
    
    # Initialize variables used for the API request and function
    base_url = "https://api.openalex.org/works/"
    params = {
        "mailto": email,
        "select": "ids,cited_by_count,updated_date",
    }

    # Initialize variables used for the API request and function
    search_results = []
    iter_count = 0
    update_count = 0
    now = datetime.now()  # Initialize 'now' variable
    
    if verbose:
        print("Reading the existing data...")

    # Load the existing data
    df = pd.read_csv(file_path)

    # Get the PMIDs from the DataFrame
    pmids = df["pmid"].tolist()

    # Get the date and time when the publications data file was last updated
    last_modification_datetime_of_pub_data = datetime.fromtimestamp(os.path.getmtime(file_path))
    if verbose:
        print(f"Publications data were last modified on {last_modification_datetime_of_pub_data}.")

    if verbose:
        print(f"Calling OpenAlex API to get updates for {len(pmids)} works...")
    for pmid in pmids:
        # Initialize variables used for each iteration
        response = None
        data = None
        url = None

        # Handle API rate limit
        if iter_count > 9:
            time_delta = datetime.now() - now
            if time_delta < timedelta(seconds=1):
                remaining_time = 1 - time_delta.total_seconds()
                if verbose:
                    print(f"Number of requests reached 10. Sleeping for {round(remaining_time, 3)} seconds...")
                time.sleep(remaining_time)
                iter_count = 0
                now = datetime.now()

        # Construct the URL for the API call
        url = f"{base_url}pmid:{pmid}"

        # Retrieve data for the work using the OpenAlex API
        try: 
            response = requests.get(url, params=params)    
        except requests.RequestException as e:
            if verbose:
                print(f"An error occurred while making an API call with PMID {pmid}: {e}")
            continue

        # Handle unsuccessful API calls    
        if response.status_code != 200: 
            if verbose:
                print(f"API call for work with PMID {pmid} was not successful. Status code: {response.status_code}")
            continue

        # Continue if the API call was successful   
        else:    
            data = response.json()
            if verbose:
                print(f"Successfully retrieved metadata for work with PMID {pmid}.")

        search_results.append(data)
        iter_count += 1  # Increment the iteration count

    if verbose:
        print("Finished calling the API. Processing the results...")


    # Check if the update_date for each search result is newer than the existing data
    for work in search_results:
        # Get the PMID and update date from the search result
        _pmid = work["ids"].get("pmid", "")
        if _pmid.startswith("http"):
            _pmid = _pmid.split("/")[-1]
        _update_date = work.get("updated_date", "")

        # Convert _update_date str to datetime format
        # Example format of the _update_date str is "2024-08-01T11:17:58.717683"
        _update_date = datetime.strptime(_update_date, "%Y-%m-%dT%H:%M:%S.%f")

        # Check if the updated date is newer than the existing data
        if not _update_date > last_modification_datetime_of_pub_data:
            if verbose:
                print(f"Data for PMID {_pmid} is up-to-date. Skipping the update.")
            continue
        else:
            # Get the citation count from the search result
            _cited_by_count = work.get("cited_by_count", "")

            # Update the citation count in the DataFrame
            if verbose:
                print(f"Data for PMID {_pmid} is outdated. Updating the citation count to {_cited_by_count}...")
            
            df.loc[df["pmid"] == _pmid, "cited_by_count"] = _cited_by_count

            if verbose:
                print(f"Update of the citation count for PMID {_pmid} is complete.")
            update_count += 1
    if verbose:
        print(f"Finished processing the results. Updated the citation counts for {update_count} articles.")

    # Save the updated DataFrame with the new citation counts to the CSV file if there were updates
    if update_count > 0:
        if verbose:
            print("Saving the updated data to the CSV file...")
        df.to_csv("../_data/articles-metadata.csv", index=False)
        if verbose:
            print("Data saved successfully.")

        # Update the log file with the new update timestamp to reflect the last update date on the bottom of the publications page
        update_log(file_path) 
    else:
        if verbose:
            print("No updates were made. Data file was not modified.")
    if verbose:
        print("Done.")

# Example usage:
# update_citation_counts(pmids, email, verbose=True) 
########################################################################################


import os
import json
from datetime import datetime

def update_log(file_path: str = "../_data/articles-metadata.csv") -> None:
    """
    Update the log file with the last modification date of the articles metadata file.

    Args:
        file_path: Path to the articles metadata file. Defaults to "../_data/articles-metadata.csv".

    Returns:
        None
    """
    # Get the last modification date of the articles metadata file
    last_modified = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime("%Y-%m-%d")

    # Create a dictionary to store the last modification date
    log_data = {
        "last_modified": last_modified
    }

    # Save the log data to a JSON file
    with open("../_data/update-log.json", "w") as file:
        json.dump(log_data, file)

# Example usage:
# update_log()
