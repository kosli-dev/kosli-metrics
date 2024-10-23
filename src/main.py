import os

import typer

import requests
from requests.auth import HTTPBasicAuth
import json
from typing import List, Dict, Any
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn


def fetch_paginated_data(base_url: str, params: Dict[str, Any] = None, api_key: str = None) -> List[Dict[str, Any]]:
    """
    Fetches all paginated data from the API and combines it into a single list.

    Args:
        base_url (str): The base URL for the API endpoint
        params (Dict[str, Any], optional): Additional query parameters to include
        api_key (str, optional): API key to use. Defaults to None.

    Returns:
        List[Dict[str, Any]]: Combined list of all data entries
    """
    if params is None:
        params = {}

    # Initialize empty list to store all data
    all_data = []
    current_page = 1

    while True:
        # Update params with current page
        request_params = {**params, 'page': current_page}

        # Make the request
        auth = None
        if api_key:
            auth = HTTPBasicAuth(api_key, '')
        response = requests.get(base_url, params=request_params, headers={'Accept': 'application/json'}, auth=auth)
        response.raise_for_status()  # Raise exception for bad status codes

        # Parse the response
        result = response.json()

        # Extract the data and pagination info
        data = result.get('data', [])
        pagination = result.get('pagination', {})

        # Add the current page's data to our collection
        all_data.extend(data)

        # Check if we've reached the last page
        if current_page >= pagination.get('page_count', 0):
            break

        # Move to next page
        current_page += 1

    return all_data


def save_to_json(data: List[Dict[str, Any]], output_file: str) -> None:
    """
    Saves the combined data to a JSON file.

    Args:
        data (List[Dict[str, Any]]): The data to save
        output_file (str): Path to the output file
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({'data': data}, f, indent=2)


def main(org: str, flow: str, output_file: str = None, from_ts: int = None, to_ts: int = None):
    api_key = os.environ.get('KOSLI_API_KEY')
    kosli_host = os.environ.get('KOSLI_HOST', "https://app.kosli.com")
    base_url = f"{kosli_host}/api/v2/attestations/{org}/{flow}"
    params = { 'from_timestamp': from_ts, 'to_timestamp': to_ts }
    try:
        # Fetch all data
        with Progress(
                BarColumn(),
                TextColumn("[progress.description]{task.description}"),
                transient=True,
        ) as progress:
            progress.add_task(description="Loading data...", total=None)
            all_data = fetch_paginated_data(base_url, params=params, api_key=api_key)

        # Save to file
        if output_file:
            save_to_json(all_data, output_file)
            print(f"Successfully saved {len(all_data)} records to {output_file}")
        else:
            print(f"Successfully read {len(all_data)} records from API")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    typer.run(main)