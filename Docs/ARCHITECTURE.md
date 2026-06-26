# TABELA Project Architecture

## Overview

TABELA is a project that aims to provide a comprehensive analysis and scoring system for ETFs based on various themes. The project is designed to help investors make informed decisions by evaluating ETFs based on their alignment with specific themes and their overall performance.

## Architecture Diagram

![TABELA Architecture Diagram](./images/tabela-architecture.png)

The above diagram provides a visual representation of the TABELA project's architecture. It shows the main components and their relationships, as well as the flow of data through the system.

## Components

1. **main.py**: The entry point of the TABELA project. It imports the `run_tabela_pipeline` function from the `core.pipeline` module and calls it when the script is executed directly.

2. **core.pipeline**: Contains the main analysis workflow of the TABELA project. The `run_tabela_pipeline` function orchestrates the execution of various steps, including ETF filtering, theme parsing, score calculation, watchlist building, and snapshot saving.

3. **core.etf_filter**: Contains functions for filtering ETFs based on specific criteria, such as market capitalization, liquidity, and sector classification.

4. **core.etf_engine**: Contains functions for retrieving ETF data from external sources, such as Yahoo Finance, and processing the data for further analysis.

5. **core.theme_parser**: Contains functions for parsing theme data and calculating ETF scores based on theme alignment.

6. **core.watchlist**: Contains functions for building a watchlist of top-performing ETFs based on their scores.

7. **core.snapshot**: Contains functions for saving the analysis results, including ETF scores and watchlist information, to a snapshot file.

## Workflow

1. **ETF Filtering**: The `core.etf_filter` module filters ETFs based on specified criteria, such as market capitalization and liquidity.

2. **ETF Data Retrieval**: The `core.etf_engine` module retrieves ETF data from external sources, such as Yahoo Finance, and processes the data for further analysis.

3. **Theme Parsing**: The `core.theme_parser` module parses theme data and calculates ETF scores based on theme alignment.

4. **Score Calculation**: The `core.theme_parser` module calculates ETF scores based on theme alignment and other criteria.

5. **Watchlist Building**: The `core.watchlist` module builds a watchlist of top-performing ETFs based on their scores.

6. **Snapshot Saving**: The `core.snapshot` module saves the analysis results, including ETF scores and watchlist information, to a snapshot file.

## Data Flow

The TABELA project relies on external data sources, such as Yahoo Finance, to retrieve ETF data. The retrieved data is then processed and analyzed using the various components of the project. The results, including ETF scores and watchlist information, are saved to a snapshot file.

## Dependencies

The TABELA project relies on the following external dependencies:

- `pandas`: A powerful data manipulation library.
- `requests`: A library for making HTTP requests.
- `beautifulsoup4`: A library for parsing HTML and XML documents.
- `yfinance`: A library for retrieving financial data from Yahoo Finance.

## Configuration

The TABELA project supports various configuration options, including:

- `ETF_FILTER_CRITERIA`: Specifies the criteria used for filtering ETFs.
- `THEME_FILE`: Specifies the file containing theme data.
- `OUTPUT_FILE`: Specifies the file where the analysis results will be saved.

## Testing

The TABELA project includes a test suite that covers various aspects of the project's functionality. To run the tests, execute the following command:
