# Phase 1 Code Guide

## Implemented modules

### `src/crimemapai/data/loader.py`
Loads one or many CSV files independently.

### `src/crimemapai/data/profile.py`
Creates:
- dataset summary;
- column profile;
- numeric profile;
- categorical profile;
- outlier profile;
- temporal profile.

### `src/crimemapai/data/grain.py`
Determines whether candidate keys are:
- unique;
- duplicated;
- null;
- 1:1;
- 1:M;
- M:1;
- M:M.

It also estimates merge row multiplication.

### `src/crimemapai/data/merge_audit.py`
Compares common columns and candidate composite keys.

### `src/crimemapai/data/report.py`
Runs the single-file profiling pipeline and exports diagnostic tables.

### `src/crimemapai/data/cli.py`
Command-line entry point.

## Example

```bash
python -m crimemapai.data.cli data/raw/file_a.csv data/raw/file_b.csv
```

## Candidate-key example

```python
from crimemapai.data.grain import compare_key

result = compare_key(
    file_a,
    file_b,
    ["state_code", "district_code", "year"],
)

print(result)
```

## Important semantic rule

A structurally valid key is not automatically a semantically valid key.

For example:

```text
id
```

can be unique in both datasets while still being independently generated.

The final merge decision requires source/documentation/meaning validation.
