import os

import typer

import requests
import json
from typing import List, Dict, Any
from rich.progress import Progress, TextColumn, BarColumn

from fetch import fetch_paginated_data


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