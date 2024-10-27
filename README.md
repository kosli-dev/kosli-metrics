# Kosli Stats

## Usage

### Download raw attestations

```
$ ./metrics download --help

 Usage: metrics download [OPTIONS]

╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  --org                TEXT     [default: None] [required]                                             │
│ *  --flow               TEXT     [default: None] [required]                                             │
│    --from-ts            INTEGER  [default: None]                                                        │
│    --to-ts              INTEGER  [default: None]                                                        │
│    --api-key            TEXT     [env var: KOSLI_API_KEY] [default: None]                               │
│    --kosli-host         TEXT     [env var: KOSLI_HOST] [default: https://app.kosli.com]                 │
│    --output-file        TEXT     [default: None]                                                        │
│    --help                        Show this message and exit.                                            │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
