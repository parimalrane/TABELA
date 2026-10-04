# TABELA Project — Agent Entry Point

## 🚨 Read These First (Mandatory)

Before writing a single line of code, any agent or developer **must** read:

1. **[AGENT_RULES.md](docs/AGENT_RULES.md)** — Operating rules, what you can and cannot change, and the config.py approval workflow.
2. **[BACKTESTING_GUIDE.md](docs/BACKTESTING_GUIDE.md)** — How to run the backtesting engine, how to design Cartesian grids, and how to interpret results.
3. **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** — Full system architecture, data flow, and engine responsibilities.
4. **[BACKTESTING_HANDOVER.md](docs/BACKTESTING_HANDOVER.md)** — Distilled knowledge from all previous backtesting sessions. Proven results. Never revert these.
5. **[FUTURE_ENHANCEMENTS.md](docs/FUTURE_ENHANCEMENTS.md)** — Pending work and unimplemented ideas.

## Strict Directory Exclusion Rules
- **DO NOT** scan, list, or read files in `.venv/`
- **DO NOT** read, analyze, or index raw data files in `market_data/`
- **DO NOT** read, analyze, or index raw data files in `.opencode/`
- Limit all code analysis strictly to source modules, configuration files, and test files

## The Single Most Important Rule

> **`config/config.py` cannot be modified during backtesting or to "fix" pipeline output.**  
> Every number in that file is the result of multi-hour grid-search regressions.  
> Any proposed config change requires explicit human authorization. See `AGENT_RULES.md`.