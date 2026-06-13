# ThemePulse

ThemePulse is a Python-based market scanning prototype for identifying attractive long and short stock opportunities by combining ETF theme strength with stock-level fundamental and technical scoring.

The project is designed around a simple idea: analyze which themes are gaining institutional attention, map stocks into those themes, score them using multiple factors, and produce ranked watchlists for further review.

## What it does

ThemePulse currently performs the following workflow:

- Loads market and ETF input data from CSV files
- Measures ETF theme strength and classifies themes as Leading, Emerging, Weakening, or Lagging
- Maps stocks to themes using a combination of manual overrides and automated mapping
- Calculates stock scores for:
  - Relative Strength (RS) raw and rating
  - Sales score
  - Zacks score
  - Margin score
  - Composite score
- Builds long and short watchlists
- Prints a console-based daily market scan summary with theme breadth and top-ranked names

## Project structure

- main.py — Main pipeline that runs the full analysis
- scoring_engine.py — RS, sales, Zacks, and margin scoring logic
- composite_engine.py — Composite score calculation
- company_theme_engine.py — Manual stock-to-theme overrides
- theme_translation_engine.py — Translation between company themes and ETF themes
- stock_mapper.py — Theme mapping logic for stocks
- watchlist_engine.py — Long watchlist generation
- short_engine.py — Short watchlist generation
- breadth_engine.py — Theme breadth analysis
- stocks.csv, etf_master.csv, ETF.csv — Input data files

## Requirements

- Python 3.9+
- pandas

Install dependencies with:

```bash
pip install -r requirements.txt
```

## Usage

From the project root, run:

```bash
python main.py
```

The script will generate a console report showing:

- Market rotation summary
- Theme breadth analysis
- Top long watchlist candidates
- Top short watchlist candidates
- Top institutional leader ideas

## Notes

This repository is a prototype and is intended for research and analysis rather than production trading execution.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
