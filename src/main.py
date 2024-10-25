import os

import numpy as np
import typer

import requests
import json
from typing import List, Dict, Any, Annotated
from rich.progress import Progress, TextColumn, BarColumn
from rich.table import Table
from rich.console import Console
import pandas as pd

from fetch import fetch_paginated_data

app = typer.Typer(no_args_is_help=True)

BECAME_NON_COMPLIANT = 'became-non-compliant'
BECAME_COMPLIANT = 'became-compliant'
STAYED_NON_COMPLIANT = 'stayed-non-compliant'
STAYED_COMPLIANT = 'stayed-compliant'

LOOKUP = {
    (False, True): BECAME_COMPLIANT,
    (True, False): BECAME_NON_COMPLIANT,
    (True, True): STAYED_COMPLIANT,
    (False, False): STAYED_NON_COMPLIANT,
    (np.nan, True): STAYED_COMPLIANT,
    (np.nan, False): BECAME_NON_COMPLIANT,
}

console = Console()

def save_to_json(data: List[Dict[str, Any]], output_file: str) -> None:
    """
    Saves the combined data to a JSON file.

    Args:
        data (List[Dict[str, Any]]): The data to save
        output_file (str): Path to the output file
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({'data': data}, f, indent=2)


# def get_last_change(group):
#     mask = ~group['event'].isin([BECAME_COMPLIANT, BECAME_NON_COMPLIANT])
#     group['last_change'] = group['created_at']
#     group.loc[mask, 'last_change'] = group['last_change'].shift(1)
#     return group


# def get_last_change(group):
#     mask = ~group['event'].isin([BECAME_COMPLIANT, BECAME_NON_COMPLIANT])
#     last_change = group['created_at'].copy()
#     last_change[mask] = last_change.shift(1)
#     return last_change

def get_last_change(group):
    # group['created_at'].where(group['event'] in [BECAME_COMPLIANT, BECAME_NON_COMPLIANT], group['created_at'], None)
    return np.where(group['event'].isin([BECAME_NON_COMPLIANT, BECAME_COMPLIANT]), group['created_at'], None)


@app.command()
def analyze(
        data_file: str = typer.Option()
) -> None:
    data = json.load(open(data_file))['data']

    df = pd.DataFrame(data)
    df['created_at'] = pd.to_datetime(df['created_at'], unit='s')
    df['date'] = df['created_at'].dt.date
    df['time'] = df['created_at'].dt.time

    df['nar_id'] = df['annotations'].apply(lambda x: x.get('NAR_ID'))
    df['repository'] = df['annotations'].apply(lambda x: x.get('REPOSITORY'))
    df['branch'] = df['git_commit_info'].apply(lambda x: x.get('branch'))

    df['prev_is_compliant'] = df.groupby(['attestation_name', 'branch'])['is_compliant'].shift(1)
    df['event'] = df.apply(lambda x : LOOKUP[(x['prev_is_compliant'], x['is_compliant'])], axis=1)


    table = Table(show_header=True, header_style="bold")

    # Add columns
    table.add_column("NAR ID")
    table.add_column("Repository")
    table.add_column("Branch")
    table.add_column("Date")
    table.add_column("Time")
    table.add_column("Compliant", justify="center")
    table.add_column("Event")

    # Add rows
    for _, row in df[[
        "nar_id", "repository", "branch", "date",
        "time", "is_compliant", "event"
    ]].iterrows():
        table.add_row(
            str(row["nar_id"]),
            str(row["repository"]),
            str(row["branch"]),
            str(row["date"]),
            str(row["time"]),
            str(row["is_compliant"]),
            str(row["event"]),
        )

    console.print(table)


@app.command()
def download(
        org: Annotated[str, typer.Option()],
        flow: Annotated[str, typer.Option()],
        from_ts: int = None,
        to_ts: int = None,
        api_key: Annotated[str, typer.Option(envvar="KOSLI_API_KEY")] = None,
        kosli_host: Annotated[str, typer.Option(envvar="KOSLI_HOST")] = "https://app.kosli.com",
        output_file: str = None
) -> None:
    try:
        # Fetch all data
        with Progress() as progress:
            all_data = fetch_paginated_data(
                base_url(flow, kosli_host, org),
                params={'from_timestamp': from_ts, 'to_timestamp': to_ts},
                api_key=api_key,
                progress=progress
            )

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


def base_url(flow, kosli_host, org):
    base_url = f"{kosli_host}/api/v2/attestations/{org}/{flow}"
    return base_url


if __name__ == "__main__":
    app()