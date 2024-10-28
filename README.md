# Kosli Stats

## Set up

You will need a working version of python3.

1. Clone this repository: `git clone https://github.com/kosli-dev/kosli-metrics.git`
2. Enter the directory: `cd kosli-metrics`
3. Install the requirements `pip install -r requirements.txt`

## Usage

### Download raw attestations

To download a JSON dump of the attestations for a specific Kosli Organization and Flow:

```
$ ./metrics download --help

 Usage: metrics download [OPTIONS] OUTPUT_FILE

╭─ Arguments ───────────────────────────────────────────────────────────────────────╮
│ *    output_file      TEXT  [default: None] [required]                            │
╰───────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ─────────────────────────────────────────────────────────────────────────╮
│ *  --org               TEXT     [default: None] [required]                        │
│ *  --flow              TEXT     [default: None] [required]                        │
│    --from-ts           INTEGER  [default: None]                                   │
│    --to-ts             INTEGER  [default: None]                                   │
│    --api-key           TEXT     [env var: KOSLI_API_KEY] [default: None]          │
│    --kosli-host        TEXT     [env var: KOSLI_HOST]                             │
│                                 [default: https://app.kosli.com]                  │
│    --help                       Show this message and exit.                       │
╰───────────────────────────────────────────────────────────────────────────────────╯
```

### Parse data

This will provide a table view of the data, or save to a CSV file with the `--out` flag.

#### Directly from API

```
$ ./metrics parse flow --help

 Usage: metrics parse flow [OPTIONS]

╭─ Options ─────────────────────────────────────────────────────────────────────────╮
│ *  --org               TEXT     [default: None] [required]                        │
│ *  --flow              TEXT     [default: None] [required]                        │
│    --from-ts           INTEGER  [default: None]                                   │
│    --to-ts             INTEGER  [default: None]                                   │
│    --api-key           TEXT     [env var: KOSLI_API_KEY] [default: None]          │
│    --kosli-host        TEXT     [env var: KOSLI_HOST]                             │
│                                 [default: https://app.kosli.com]                  │
│    --out               TEXT     [default: None]                                   │
│    --help                       Show this message and exit.                       │
╰───────────────────────────────────────────────────────────────────────────────────╯
```

### From a previously downloaded JSON file

```
$ ./metrics parse file --help

Usage: metrics parse file [OPTIONS] DATA_FILE

╭─ Arguments ───────────────────────────────────────────────────────────────────────╮
│ *    data_file      TEXT  [default: None] [required]                              │
╰───────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ─────────────────────────────────────────────────────────────────────────╮
│ --out         TEXT  [default: None]                                               │
│ --help              Show this message and exit.                                   │
╰───────────────────────────────────────────────────────────────────────────────────╯
```