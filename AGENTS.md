# Project Scope Rules

## Strict Directory Exclusion Rules
- **DO NOT** scan, list, or read files in `.venv/`.
- **DO NOT** read, analyze, or index raw data files in `market_data/`.
- **DO NOT** read, analyze, or index raw data files in `.opencode/`.
- Limit all code analysis, tool executions, and file searches strictly to source modules, configuration files, and test files (e.g., root `.py` files, `tests/`).