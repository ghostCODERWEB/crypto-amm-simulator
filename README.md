# Constant-product AMM simulator

Simulate integer reserve swaps, liquidity minting, fees and price impact without RPC access.

This is an original, AI-assisted reference implementation. It is a local research tool, with synthetic fixtures and no external network, wallet, signing, deployment, or custody functionality. Version 0.1.0 is a foundation for further development, not an audited protocol or production financial system.

## Run

Requires Python 3.11 or newer. Runtime uses only the standard library.

```sh
python3 -m cryptolab examples/input.json
python3 -m cryptolab examples/input.json --format csv --output result.csv
python3 -m unittest discover -s tests -v
```

Optional installation: `python3 -m pip install -e .`. The installed command is `crypto-amm-simulator`. These repositories each use the package name `cryptolab`; install each in its own virtual environment.

## Features

- A deterministic domain engine exposed as `cryptolab.analyze(data)`.
- An executable JSON fixture and checked expected output.
- JSON and flattened CSV export with atomic file replacement.
- Strict JSON parsing rejects duplicate keys and non-finite constants.
- Domain-specific regression tests plus CLI, input integrity and export tests.
- CI on Python 3.11, 3.12, 3.13 and 3.14.

## Input and output

See [the input fixture](examples/input.json), [expected output](examples/expected.json) and [input reference](docs/input-reference.md). Numeric units, time conventions and limitations are recorded in [architecture](docs/architecture.md).

## Development

Run tests before changing behavior. Add a fixture and a regression test for each new case. Public functions raise `ValueError` for invalid domain values; missing fields raise `KeyError`. CLI errors exit with status 2 and leave the output file untouched.

See [contributing](CONTRIBUTING.md), [security](SECURITY.md), and [roadmap](docs/roadmap.md). MIT licensed.

## Browser dashboard

```sh
python3 -m cryptolab.server --port 8787 --db runs.sqlite3
```

Open `http://127.0.0.1:8787`. The dashboard provides editable JSON inputs, imports, saved run history, batch execution, scenario comparisons and JSON exports. Use different ports to run multiple laboratories. SQLite stores snapshots locally; the database is gitignored.

Scenario mode accepts `[{'name': 'stress', 'patches': [{'path': '/field', 'value': 123}]}]` using JSON double quotes. Paths use JSON Pointer escaping and must exist. Every scenario starts independently from the baseline; failures are reported per case. Batch mode accepts an array of up to 100 input objects.

The server binds exclusively to loopback. Mutation and history requests require a per-session token; Host checks and browser origin checks constrain cross-origin access. It is a local development application, not a public hosting service. Do not expose it with a tunnel.

See [dashboard and API](docs/dashboard.md) for routes, limits and persistence behavior.
