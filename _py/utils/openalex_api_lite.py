"""
OpenAlex API Utilities (Minimal Version)
========================================

A lightweight module for retrieving scholarly work metadata from the OpenAlex API.
This streamlined version focuses on metadata retrieval and Jupyter notebook display,
removing PDF downloading, caching, and visualization dependencies.

Dependencies:
    - httpx: Modern HTTP client for API requests (replaces requests)
    - tqdm: Progress bar display
    - IPython.display: Rich display in Jupyter notebooks

Async Support:
    This module uses synchronous httpx calls by default. For async usage,
    see the commented async patterns throughout the code. Key changes needed:
    
    1. Use `async with httpx.AsyncClient() as client:` instead of direct calls
    2. Change `httpx.get()` to `await client.get()`
    3. Add `async` keyword to function definitions
    4. Use `asyncio.run()` or `await` to call async functions
    
    Example async usage:
        >>> import asyncio
        >>> async def main():
        ...     works, failed = await get_works_async(
        ...         ids=["38857748"],
        ...         email="your.email@example.com"
        ...     )
        ...     return works
        >>> works = asyncio.run(main())

Example:
    >>> from openalex_api_utils import get_works, list_works
    >>> works, failed = get_works(
    ...     ids=["38857748", "10.1186/s12967-023-04576-8"],
    ...     email="your.email@example.com",
    ...     show_progress=True
    ... )
    >>> list_works(works)
"""

import os
import re
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple

import httpx
# ASYNC: Also import asyncio for async support
# import asyncio
from tqdm import tqdm
# ASYNC: For async progress bars, use tqdm.asyncio
# from tqdm.asyncio import tqdm as atqdm
from IPython.display import display, HTML


# =============================================================================
# Core API Function
# =============================================================================

def get_works(
    ids: List[str],
    email: str,
    select_fields: str = (
        "id,doi,title,authorships,publication_year,publication_date,ids,"
        "primary_location,type,open_access,has_fulltext,cited_by_count,"
        "biblio,primary_topic,topics,keywords,concepts,mesh,"
        "best_oa_location,referenced_works,related_works,cited_by_api_url,"
        "counts_by_year,updated_date,created_date,type_crossref"
    ),
    show_progress: bool = False,
    verbose: bool = False
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Retrieve metadata for scholarly works from the OpenAlex API.

    Works are scholarly documents like journal articles, books, datasets, and
    theses. This function accepts multiple identifier formats and returns
    structured metadata for each work.

    Args:
        ids: List of work identifiers. Accepts:
            - PubMed IDs (PMID): e.g., "38857748"
            - PubMed Central IDs (PMCID): e.g., "PMC9046468"
            - DOIs: e.g., "10.1186/s12967-023-04576-8"
            - OpenAlex IDs: e.g., "W1997963236" or full URL
        email: Email address for API requests (required by OpenAlex for polite pool).
        select_fields: Comma-separated list of fields to retrieve from the API.
            See https://docs.openalex.org/api-entities/works for available fields.
        show_progress: If True, displays a tqdm progress bar. Disables verbose output.
        verbose: If True, prints detailed status messages. Ignored if show_progress is True.

    Returns:
        A tuple containing:
            - works: List of dictionaries with work metadata. Each dict contains:
                - "uid": The original identifier used for the request
                - "metadata": The full API response for the work
                - "status_messages": Log of operations performed
            - failed_calls: List of dictionaries describing failed API requests,
              including the uid, status_code, and error message.

    Raises:
        AssertionError: If email is not provided or ids is not a list.

    Example:
        >>> works, failed_calls = get_works(
        ...     ids=["38857748", "10.1186/s12967-023-04576-8"],
        ...     email=os.environ.get("EMAIL"),
        ...     show_progress=True
        ... )
        >>> print(f"Retrieved {len(works)} works, {len(failed_calls)} failed")

    Note:
        The OpenAlex API has a rate limit of 10 requests per second. This function
        automatically handles rate limiting by sleeping when necessary.
    """
    # Input validation
    assert email, "Please provide your email to use the OpenAlex API."
    assert ids, "Please provide a list of IDs to retrieve data."
    assert isinstance(ids, list), "IDs must be provided as a list."
    assert isinstance(show_progress, bool), "show_progress must be a boolean value."
    assert isinstance(verbose, bool), "verbose must be a boolean value."

    # API configuration
    base_url = "https://api.openalex.org/works/"
    params = {
        "mailto": email,
        "select": select_fields,
    }

    # Initialize result containers
    works: List[Dict[str, Any]] = []
    failed_calls: List[Dict[str, Any]] = []

    # Regex pattern for DOI detection
    doi_regex = r"10.\d{1,9}/[-._;()/:A-Za-z0-9]+"

    # Rate limiting variables
    todays_date = datetime.now().date()
    now = datetime.now()
    iter_count = 0

    # Configure iteration with optional progress bar
    if show_progress:
        iterable = tqdm(ids, desc="Retrieving works")
        verbose = False  # Disable verbose output when progress bar is active
    else:
        iterable = ids

    # Process each identifier
    for id in iterable:
        # Initialize per-iteration variables
        response = None
        data = None
        url = None
        status_message = ""

        # Normalize ID by removing URL prefixes
        if id.startswith("https://openalex.org/") or id.startswith("https://api.openalex.org/"):
            id = id.split("/")[-1]
        if id.startswith("https://doi.org/"):
            id = id.replace("https://doi.org/", "")

        if verbose:
            print("---")

        # Rate limiting: OpenAlex allows 10 requests per second
        # ASYNC: Replace time.sleep() with await asyncio.sleep()
        if iter_count > 9:
            time_delta = datetime.now() - now
            if time_delta < timedelta(seconds=1):
                remaining_time = 1 - time_delta.total_seconds()
                if verbose:
                    print(f"Rate limit reached. Sleeping for {round(remaining_time, 3)} seconds...")
                time.sleep(remaining_time)  # ASYNC: await asyncio.sleep(remaining_time)
                iter_count = 0
                now = datetime.now()

        # Construct API URL based on identifier type
        if re.match(doi_regex, id):
            url = f"{base_url}https://doi.org/{id}"
        elif id.isdigit():
            url = f"{base_url}pmid:{id}"
        elif id.startswith("PMC"):
            url = f"{base_url}pmcid:{id}"
        elif id.startswith("W"):
            url = f"https://api.openalex.org/works/{id}"
        else:
            if verbose:
                print(f"Invalid ID: {id}. Skipping...")
            failed_calls.append({"uid": id, "error": "Invalid ID format"})
            continue

        # Make API request
        # ---------------------------------------------------------------------
        # ASYNC: Replace the synchronous call below with:
        #
        #   async with httpx.AsyncClient() as client:
        #       response = await client.get(url, params=params)
        #
        # Or, for better performance with many requests, create the client once
        # outside the loop:
        #
        #   async def get_works_async(...):
        #       async with httpx.AsyncClient() as client:
        #           tasks = [fetch_one(client, id, params) for id in ids]
        #           results = await asyncio.gather(*tasks, return_exceptions=True)
        #
        #   async def fetch_one(client, id, params):
        #       response = await client.get(url, params=params)
        #       return response.json()
        # ---------------------------------------------------------------------
        try:
            response = httpx.get(url, params=params)
        except httpx.RequestError as e:
            if verbose:
                print(f"Request error for UID {id}: {e}")
            failed_calls.append({"uid": id, "error": f"Request exception: {e}"})
            continue

        # Handle unsuccessful responses
        if response.status_code != 200:
            try:
                response_data = response.json()
                error = response_data.get("error", "Unknown error")
                error_msg = response_data.get("message", "No message")
                failed_calls.append({
                    "uid": id,
                    "status_code": response.status_code,
                    "error": error,
                    "message": error_msg
                })
            except json.JSONDecodeError:
                failed_calls.append({
                    "uid": id,
                    "status_code": response.status_code,
                    "error": "JSONDecodeError"
                })
            if verbose:
                print(f"API call for UID {id} failed. Status: {response.status_code}")
            continue

        # Process successful response
        data = response.json()
        status_message = f"{todays_date}: Successfully retrieved metadata for UID {id}."
        if verbose:
            print(status_message)

        # Build work dictionary
        work = {
            "uid": id,
            "metadata": data,
            "status_messages": status_message,
        }

        works.append(work)
        iter_count += 1

    if verbose:
        print("***\nFinished retrieving works.\n")

    return works, failed_calls


# =============================================================================
# Jupyter Display Utilities
# =============================================================================

def list_works(works: List[Dict[str, Any]]) -> None:
    """
    Display work metadata in a formatted HTML view for Jupyter notebooks.

    Renders each work with title, authors, journal, citation count, and links
    to full text and PDF when available. Uses visual indicators for open access
    status and full text availability.

    Args:
        works: List of work dictionaries as returned by get_works().
            Each dictionary must contain a "metadata" key with the API response.

    Returns:
        None. Output is displayed directly in the Jupyter notebook.

    Example:
        >>> works, _ = get_works(ids=["38857748"], email="user@example.com")
        >>> list_works(works)

    Note:
        Visual indicators used:
            - 🔓 Open access
            - 🔒 Not open access
            - 📖 Full text available
            - 📑 Full text not available
    """
    for work in works:
        metadata = work["metadata"]

        # Extract basic metadata
        first_author_last_name = metadata["authorships"][0]["author"]["display_name"].split(" ")[-1]
        title = metadata["title"]
        publication_year = metadata["publication_year"]

        # Handle potentially missing primary_location
        try:
            journal = metadata["primary_location"]["source"]["display_name"]
        except (KeyError, TypeError):
            journal = "Unknown Journal"

        # Handle potentially missing primary_topic
        try:
            primary_topic = metadata["primary_topic"]["display_name"]
            primary_topic_score = metadata["primary_topic"]["score"]
        except (KeyError, TypeError):
            primary_topic = "Not available"
            primary_topic_score = "N/A"

        # Citation information
        cited_by_api_url = metadata.get("cited_by_api_url", "")
        cited_by_ui_url = cited_by_api_url.replace("api.openalex.org", "openalex.org")
        cited_by_count = metadata.get("cited_by_count", 0)

        # Full text and open access status
        has_fulltext = metadata.get("has_fulltext", False)
        is_oa = metadata.get("open_access", {}).get("is_oa", False)

        # PDF and landing page URLs
        try:
            pdf_url = metadata["best_oa_location"]["pdf_url"]
        except (KeyError, TypeError):
            pdf_url = None

        try:
            landing_page_url = metadata["best_oa_location"]["landing_page_url"]
        except (KeyError, TypeError):
            landing_page_url = None

        # Reference counts
        referenced_works_count = len(metadata.get("referenced_works", []))
        related_works_count = len(metadata.get("related_works", []))

        # Visual indicators
        open_lock = "\U0001F513"   # 🔓
        closed_lock = "\U0001F512" # 🔒
        full_text_icon = "\U0001F4D6"    # 📖
        no_full_text_icon = "\U0001F4D1" # 📑

        # Build HTML links
        pdf_link = f"<a href='{pdf_url}' target='_blank'>Download PDF</a>" if pdf_url else "PDF not available"
        full_text_link = f"<a href='{landing_page_url}' target='_blank'>Read Full Text</a>" if landing_page_url else "Full text not available"

        # Render HTML output
        display(
            HTML(f"{first_author_last_name} <i>et al.</i> <b>{title}.</b> {journal} {publication_year}"),
            HTML(f"<a href='{cited_by_ui_url}'>Cited by</a>: {cited_by_count} | "
                 f"References: {referenced_works_count} | Related works: {related_works_count}"),
            HTML(f"Primary topic: {primary_topic} (Score: {primary_topic_score})"),
            HTML(f"{pdf_link} &nbsp; {full_text_link} &nbsp; "
                 f"{open_lock if is_oa else closed_lock} &nbsp; "
                 f"{full_text_icon if has_fulltext else no_full_text_icon}"),
            HTML("<hr>")
        )


def get_open_access_ids(works: List[Dict[str, Any]]) -> List[str]:
    """
    Filter works to return only those that are open access.

    Args:
        works: List of work dictionaries as returned by get_works().

    Returns:
        List of OpenAlex IDs for works where open_access.is_oa is True.

    Example:
        >>> works, _ = get_works(ids=["38857748", "12345678"], email="user@example.com")
        >>> oa_ids = get_open_access_ids(works)
        >>> print(f"Found {len(oa_ids)} open access works")
    """
    open_access_ids = []
    for work in works:
        try:
            if work["metadata"]["open_access"]["is_oa"]:
                open_access_ids.append(work["metadata"]["id"])
        except (KeyError, TypeError):
            continue  # Skip works without open access metadata

    return open_access_ids


# =============================================================================
# ASYNC VERSION (Reference Implementation)
# =============================================================================
# Uncomment and use this version for concurrent API requests.
# This can significantly speed up retrieval when fetching many works.
#
# Required additional import at top of file:
#   import asyncio
#
# Usage:
#   >>> import asyncio
#   >>> works, failed = asyncio.run(get_works_async(
#   ...     ids=["38857748", "12345678", "87654321"],
#   ...     email="user@example.com"
#   ... ))
#
# In Jupyter notebooks, use:
#   >>> works, failed = await get_works_async(ids=[...], email="...")
# -----------------------------------------------------------------------------
#
# async def get_works_async(
#     ids: List[str],
#     email: str,
#     select_fields: str = (
#         "id,doi,title,authorships,publication_year,publication_date,ids,"
#         "primary_location,type,open_access,has_fulltext,cited_by_count,"
#         "biblio,primary_topic,topics,keywords,concepts,mesh,"
#         "best_oa_location,referenced_works,related_works,cited_by_api_url,"
#         "counts_by_year,updated_date,created_date,type_crossref"
#     ),
#     max_concurrent: int = 10,  # Respect OpenAlex rate limit
#     verbose: bool = False
# ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
#     """
#     Async version of get_works() for concurrent API requests.
#     
#     Args:
#         ids: List of work identifiers (PMID, PMCID, DOI, or OpenAlex ID).
#         email: Email address for API requests.
#         select_fields: Comma-separated list of fields to retrieve.
#         max_concurrent: Maximum concurrent requests (default 10 for rate limit).
#         verbose: If True, prints status messages.
#     
#     Returns:
#         Tuple of (works, failed_calls) lists.
#     """
#     import asyncio
#     
#     base_url = "https://api.openalex.org/works/"
#     params = {"mailto": email, "select": select_fields}
#     doi_regex = r"10.\d{1,9}/[-._;()/:A-Za-z0-9]+"
#     
#     works: List[Dict[str, Any]] = []
#     failed_calls: List[Dict[str, Any]] = []
#     semaphore = asyncio.Semaphore(max_concurrent)
#     
#     async def fetch_one(client: httpx.AsyncClient, id: str) -> Dict[str, Any] | None:
#         """Fetch a single work with rate limiting via semaphore."""
#         async with semaphore:
#             # Normalize ID
#             if id.startswith("https://openalex.org/") or id.startswith("https://api.openalex.org/"):
#                 id = id.split("/")[-1]
#             if id.startswith("https://doi.org/"):
#                 id = id.replace("https://doi.org/", "")
#             
#             # Construct URL based on ID type
#             if re.match(doi_regex, id):
#                 url = f"{base_url}https://doi.org/{id}"
#             elif id.isdigit():
#                 url = f"{base_url}pmid:{id}"
#             elif id.startswith("PMC"):
#                 url = f"{base_url}pmcid:{id}"
#             elif id.startswith("W"):
#                 url = f"https://api.openalex.org/works/{id}"
#             else:
#                 failed_calls.append({"uid": id, "error": "Invalid ID format"})
#                 return None
#             
#             try:
#                 response = await client.get(url, params=params)
#                 
#                 if response.status_code == 200:
#                     data = response.json()
#                     return {
#                         "uid": id,
#                         "metadata": data,
#                         "status_messages": f"Successfully retrieved metadata for UID {id}."
#                     }
#                 else:
#                     failed_calls.append({
#                         "uid": id,
#                         "status_code": response.status_code,
#                         "error": response.json().get("error", "Unknown error")
#                     })
#                     return None
#                     
#             except httpx.RequestError as e:
#                 failed_calls.append({"uid": id, "error": f"Request exception: {e}"})
#                 return None
#     
#     # Execute all requests concurrently
#     async with httpx.AsyncClient() as client:
#         tasks = [fetch_one(client, id) for id in ids]
#         results = await asyncio.gather(*tasks)
#     
#     # Filter out None results (failed requests)
#     works = [r for r in results if r is not None]
#     
#     if verbose:
#         print(f"Retrieved {len(works)} works, {len(failed_calls)} failed")
#     
#     return works, failed_calls
