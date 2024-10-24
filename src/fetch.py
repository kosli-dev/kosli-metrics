from typing import Dict, Any, List

import requests
from requests.auth import HTTPBasicAuth


def fetch_paginated_data(base_url: str, params: Dict[str, Any] = None, api_key: str = None, progress=None) -> List[Dict[str, Any]]:
    """
    Fetches all paginated data from the API and combines it into a single list.

    Args:
        base_url (str): The base URL for the API endpoint
        params (Dict[str, Any], optional): Additional query parameters to include
        api_key (str, optional): API key to use. Defaults to None.

    Returns:
        List[Dict[str, Any]]: Combined list of all data entries
        :param progress:
    """
    if params is None:
        params = {}

    # Initialize empty list to store all data
    all_data = []
    current_page = 1

    task_id = None
    if progress:
        task_id = progress.add_task(description="Loading data...", total=None)

    while True:
        # Update params with current page
        request_params = {**params, 'page': current_page}

        # Make the request
        response = requests.get(
            base_url,
            params=request_params,
            headers={'Accept': 'application/json'},
            auth=make_auth(api_key)
        )
        response.raise_for_status()  # Raise exception for bad status codes

        # Parse the response
        result = response.json()

        # Extract the data and pagination info
        data = result.get('data', [])
        pagination = result.get('pagination', {})
        page_count = pagination.get('page_count', 0)
        if task_id is not None:
            progress.update(task_id, total=page_count, advance=1)

        # Add the current page's data to our collection
        all_data.extend(data)

        # Check if we've reached the last page
        if current_page >= page_count:
            break

        # Move to next page
        current_page += 1

    return all_data


def make_auth(api_key):
    auth = None
    if api_key:
        auth = HTTPBasicAuth(api_key, '')
    return auth
