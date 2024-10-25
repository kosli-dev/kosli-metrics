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

parse_app = typer.Typer()
app.add_typer(parse_app, name="parse")


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


@parse_app.command()
def flow(
        org: Annotated[str, typer.Option()],
        flow: Annotated[str, typer.Option()],
        from_ts: int = None,
        to_ts: int = None,
        api_key: Annotated[str, typer.Option(envvar="KOSLI_API_KEY")] = None,
        kosli_host: Annotated[str, typer.Option(envvar="KOSLI_HOST")] = "https://app.kosli.com",
        out: str = None
) -> None:
    with Progress() as progress:
        data = fetch_paginated_data(
            base_url(flow, kosli_host, org),
            params={'from_timestamp': from_ts, 'to_timestamp': to_ts},
            api_key=api_key,
            progress=progress
        )

    df = create_data_frame(data)
    columns = [
        "nar_id", "repository", "branch", "date",
        "time", "is_compliant", "event"
    ]
    render_data_frame(df, columns, out)


@parse_app.command()
def file(
        data_file: str,
        out: str = None
) -> None:
    data = json.load(open(data_file))['data']
    df = create_data_frame(data)
    columns = [
        "nar_id", "repository", "branch", "date",
        "time", "is_compliant", "event"
    ]
    render_data_frame(df, columns, out)


def render_data_frame(df, columns, out):
    if out is None:
        print_table(df, columns)
    else:
        df[columns].to_csv(out, index=False)


def print_table(df, columns):
    table = Table(show_header=True, header_style="bold")
    # Add columns
    for column in columns:
        table.add_column(column)
    # Add rows
    for _, row in df[columns].iterrows():
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


def create_data_frame(data):
    df = pd.DataFrame(data)
    df['created_at'] = pd.to_datetime(df['created_at'], unit='s')
    df['date'] = df['created_at'].dt.date
    df['time'] = df['created_at'].dt.time
    df['nar_id'] = df['annotations'].apply(lambda x: x.get('NAR_ID'))
    df['repository'] = df['annotations'].apply(lambda x: x.get('REPOSITORY'))
    df['branch'] = df['git_commit_info'].apply(lambda x: x.get('branch'))
    df['prev_is_compliant'] = df.groupby(['attestation_name', 'branch'])['is_compliant'].shift(1)
    df['event'] = df.apply(lambda x: LOOKUP[(x['prev_is_compliant'], x['is_compliant'])], axis=1)
    return df


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
    return f"{kosli_host}/api/v2/attestations/{org}/{flow}"


if __name__ == "__main__":
    app()