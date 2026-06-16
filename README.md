# ThemePulse

ThemePulse is a Python-based market scanning prototype for identifying attractive long and short stock opportunities by combining ETF theme strength with stock-level fundamental and technical scoring.

The project is designed around a simple idea: analyze which themes are gaining institutional attention through curated ETF analysis, map stocks into those themes, score them using multiple factors, and produce ranked watchlists including institutional leader candidates for further review.

## What it does

ThemePulse currently performs the following workflow:

1. **ETF Processing**
   - Loads ETF universe from ETF.csv
   - Filters to curated whitelist via allowed_etfs.py
   - Excludes non-equity products (bonds, leveraged, inverse, etc.)
   - Maps ETFs to canonical themes
   - Calculates ETF relative strength rankings

2. **Theme Classification**
   - Classifies themes as Leading (top 25%), Emerging (25-50%), Weakening (50-75%), or Lagging (bottom 25%)
   - Assigns theme scores based on institutional ETF participation

3. **Stock Analysis**
   - Maps stocks to themes using manual overrides (company_theme_engine.py) + automated sector mapping
   - Translates company narratives to ETF-recognized themes
   - Calculates multiple stock scores:
     - Relative Strength (RS) raw and rating
     - Sales growth score
     - Zacks rank score
     - Margin score
     - Composite score (weighted combination)

4. **Watchlist Generation**
   - Builds long watchlist from Leading/Emerging themes with strong fundamentals
   - Builds short watchlist from Weakening/Lagging themes with weak technicals
   - Generates institutional leader candidates (top 20 stocks from strong themes)
   - Merges and deduplicates all candidate sources

5. **Output Reporting**
   - Displays market rotation summary (Leading/Emerging/Weakening/Lagging themes)
   - Shows theme breadth analysis with strong stock participation %
   - Lists top 40 long candidates (institutional leaders marked with *)
   - Lists top 20 short candidates
   - Annotates stocks added only through institutional flow with asterisk

## Project structure

**Core Pipeline**
- main.py — Main execution engine; orchestrates full analysis workflow

**Engine Modules**
- etf_engine.py — ETF validation, filtering, and theme classification
- stock_mapper.py — Automated stock-to-theme mapping via sector/industry
- company_theme_engine.py — Manual high-conviction stock-to-theme overrides
- theme_translation_engine.py — Translates company narratives to ETF themes
- scoring_engine.py — RS raw/rating, sales, Zacks, and margin scoring
- composite_engine.py — Weighted composite score calculation
- watchlist_engine.py — Long watchlist candidate selection
- short_engine.py — Short watchlist candidate selection
- breadth_engine.py — Theme participation breadth analysis
- institutional_leaders_engine.py — Top institutional leader selection from strong themes

**Configuration & Data**
- allowed_etfs.py — Curated whitelist of equity ETFs for analysis
- config.py — Theme classification rules and scoring parameters
- theme_parser.py — Parsing of ETF investment strategy text
- theme_dictionary.py — Theme taxonomy reference
- stocks.csv — Daily stock universe input
- ETF.csv — Daily ETF universe input

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
