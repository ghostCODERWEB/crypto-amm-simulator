# Input reference

The canonical executable example is `examples/input.json`. Amounts are synthetic units; do not infer token decimals. Unix-like integer timestamps share one caller-selected time unit. No wall clock is read by the engine.

| Field | JSON representation | Example |
|---|---|---|
| `reserve_x` | `int` | 1000000 |
| `reserve_y` | `int` | 2000000 |
| `lp_supply` | `int` | 1000000 |
| `actions` | `list` | [{"type": "swap", "direction": "x_to_y", "amount": 10000}] |

Nested structures follow the complete fixture. Fields must match the engine function documented in `cryptolab/__init__.py`. Extra JSON fields are ignored unless consumed by the domain engine. The fixture is not a formal schema.

## Output contract

`analyze(data)` returns a JSON-compatible dictionary. Decimal calculations are serialized as strings, integer token calculations as integers. CSV represents every scalar as a `(path, value)` pair; arrays use zero-based bracket indexes. `examples/expected.json` records the exact output for the fixture.

## Failure behavior

Malformed JSON, duplicate object keys, invalid constants, missing required fields and invalid domain values produce exit status 2. Python callers receive the underlying exception. A destination file is replaced only after successful calculation and serialization.
