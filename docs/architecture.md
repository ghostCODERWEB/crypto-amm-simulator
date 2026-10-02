# Architecture and assumptions

## Data flow

Input file → strict JSON parser → domain engine → serializer → stdout or atomic file replacement. The domain engine operates on caller-provided data. All prices and balances are supplied snapshots; the tool establishes no external authenticity.

## Domain

Simulate integer reserve swaps, liquidity minting, fees and price impact without RPC access.

The implementation and domain tests are the executable specification. Input units must be consistent across records. Integer token engines round down unless an explicit ceiling calculation appears in the engine. Decimal engines avoid binary floating point; input decimal strings are preferred. Every replay starts from the provided fixture/state rather than live chain data.

## Trust boundaries

Files and identifiers are caller controlled. This tool does not verify signatures, consensus, real chain finality, economic solvency or authoritative oracle prices. Inputs are read into memory; avoid unbounded untrusted datasets. CLI output can contain account identifiers supplied in the input.

## Persistence

The reorg indexer supports SQLite through its `Indexer` class. Other engines are deterministic in-memory calculations. Atomic exports prevent partial replacement during normal write failures; they are not a multi-file transactional database.

## Verification

Tests cover domain behavior and failures, determinism, subprocess execution, CSV structure, atomic output and preservation of the input object. CI tests four Python versions. Tests are regression evidence, not an audit or proof of completeness.
