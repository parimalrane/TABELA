import pandas as pd
import math
from typing import Dict, Any, Tuple, List
from datetime import datetime
import os
import re

SPDR_MAP = {
    'XLK': 'Technology', 'XLY': 'Discretionary', 'XLC': 'Communications',
    'XLF': 'Financials', 'XLP': 'Staples', 'XLU': 'Utilities',
    'XLV': 'Health Care', 'XLE': 'Energy', 'XLB': 'Materials',
    'XLI': 'Industrials', 'XLRE': 'Real Estate'
}

def get_historical_etf_path(current_path: str, days_back: int = 7) -> str:
    from datetime import datetime, timedelta
    import glob
    
    if not current_path or not os.path.exists(current_path):
        return None
        
    match = re.search(r'(\d{8})_ETF\.csv', str(current_path))
    if not match:
        return None
        
    current_date_str = match.group(1)
    current_date = datetime.strptime(current_date_str, "%Y%m%d")
    target_date = current_date - timedelta(days=days_back)
    
    base_dir = os.path.dirname(os.path.dirname(current_path))
    month_folder = target_date.strftime("%Y-%m")
    target_dir = os.path.join(base_dir, month_folder)
    
    if not os.path.exists(target_dir):
        # Walk back another month if needed
        target_date = target_date.replace(day=1) - timedelta(days=1)
        month_folder = target_date.strftime("%Y-%m")
        target_dir = os.path.join(base_dir, month_folder)
        if not os.path.exists(target_dir):
            return None
            
    # Find closest file on or before target date
    files = sorted(glob.glob(os.path.join(target_dir, "*_ETF.csv")), reverse=True)
    target_date_str = target_date.strftime("%Y%m%d")
    
    for f in files:
        f_match = re.search(r'(\d{8})_ETF\.csv', f)
        if f_match and f_match.group(1) <= target_date_str:
            return f
            
    return files[0] if files else None

class SectorIntelligence:
    def __init__(self, current_etf_path: str, historical_etf_path: str = None):
        """
        Initializes the SectorIntelligence engine using point-in-time ETF files.
        :param current_etf_path: Path to the current day's _ETF.csv
        :param historical_etf_path: Optional path to a past _ETF.csv to measure momentum rotation.
        """
        self.current_etf_path = current_etf_path
        self.historical_etf_path = historical_etf_path
        self.current_df = self._load_csv(self.current_etf_path)
        self.historical_df = self._load_csv(self.historical_etf_path) if historical_etf_path else None

    def _load_csv(self, path: str) -> pd.DataFrame:
        if not path or not os.path.exists(path):
            return pd.DataFrame()
        try:
            return pd.read_csv(path, encoding='utf-16')
        except UnicodeError:
            try:
                return pd.read_csv(path, encoding='utf-8')
            except Exception:
                return pd.DataFrame()

    def generate_intelligence_report(self, top_n: int = 3, bottom_n: int = 3) -> Dict[str, Any]:
        """
        Generates sector strength scores, excess returns vs SPY, and rotation changes.
        """
        if self.current_df.empty:
            return {}

        df = self.current_df.copy()
        hist_df = self.historical_df.copy() if self.historical_df is not None else pd.DataFrame()

        # Isolate SPY returns for baseline Relative Strength calculation
        spy_1m = 0.0
        spy_row = df[df['Ticker'] == 'SPY']
        if not spy_row.empty:
            spy_val = pd.to_numeric(spy_row.iloc[0].get("Performance 1M (%)", 0), errors='coerce')
            if pd.notna(spy_val):
                spy_1m = spy_val

        sector_data = []

        for ticker, name in SPDR_MAP.items():
            row_eval = df[df['Ticker'] == ticker]
            if row_eval.empty:
                continue
                
            row = row_eval.iloc[0]
            
            p1w = pd.to_numeric(row.get("Performance 1W (%)", 0), errors='coerce')
            p1m = pd.to_numeric(row.get("Performance 1M (%)", 0), errors='coerce')
            p3m = pd.to_numeric(row.get("Performance 3M (%)", 0), errors='coerce')
            pytd = pd.to_numeric(row.get("Performance YTD (%)", row.get("Performance 1Y (%)", 0)), errors='coerce')
            
            p1w = p1w if pd.notna(p1w) else 0.0
            p1m = p1m if pd.notna(p1m) else 0.0
            p3m = p3m if pd.notna(p3m) else 0.0
            pytd = pytd if pd.notna(pytd) else 0.0

            # Sector Strength Score Logic
            # Using configurable weights to build composite score (e.g., heavily weighting 1M and 1Q)
            w_1w, w_1m, w_3m, w_ytd = 0.2, 0.4, 0.3, 0.1
            composite_score = (p1w * w_1w) + (p1m * w_1m) + (p3m * w_3m) + (pytd * w_ytd)

            excess_vs_spy_1m = p1m - spy_1m

            # Default historical rank/score to current if history is missing 
            # We will calculate ranks properly afterwards across the whole dataset
            sector_data.append({
                'Ticker': ticker,
                'Name': name,
                '1W': p1w,
                '1M': p1m,
                '3M': p3m,
                'YTD': pytd,
                'Score': composite_score,
                'Excess_1M': excess_vs_spy_1m,
                'Historical_Score': 0.0 # Placeholder
            })

        result_df = pd.DataFrame(sector_data)
        if result_df.empty:
            return {}

        if not hist_df.empty:
             for idx, s_row in result_df.iterrows():
                 t = s_row['Ticker']
                 h_row_eval = hist_df[hist_df['Ticker'] == t]
                 if not h_row_eval.empty:
                     h_row = h_row_eval.iloc[0]
                     h1w = pd.to_numeric(h_row.get("Performance 1W (%)", 0), errors='coerce')
                     h1w = h1w if pd.notna(h1w) else 0.0
                     h1m = pd.to_numeric(h_row.get("Performance 1M (%)", 0), errors='coerce')
                     h1m = h1m if pd.notna(h1m) else 0.0
                     h3m = pd.to_numeric(h_row.get("Performance 3M (%)", 0), errors='coerce')
                     h3m = h3m if pd.notna(h3m) else 0.0
                     hytd = pd.to_numeric(h_row.get("Performance YTD (%)", h_row.get("Performance 1Y (%)", 0)), errors='coerce')
                     hytd = hytd if pd.notna(hytd) else 0.0
                     
                     w_1w, w_1m, w_3m, w_ytd = 0.2, 0.4, 0.3, 0.1
                     hist_score = (h1w * w_1w) + (h1m * w_1m) + (h3m * w_3m) + (hytd * w_ytd)
                     result_df.at[idx, 'Historical_Score'] = hist_score
                 else:
                     result_df.at[idx, 'Historical_Score'] = s_row['Score']

        # Rank based on current score
        result_df['Rank'] = result_df['Score'].rank(ascending=False, method='min')
        
        # Rank based on historical score
        if 'Historical_Score' in result_df.columns:
            result_df['Historical_Rank'] = result_df['Historical_Score'].rank(ascending=False, method='min')
            result_df['Rank_Delta'] = result_df['Historical_Rank'] - result_df['Rank'] # Positive means improved
        else:
            result_df['Rank_Delta'] = 0

        result_df = result_df.sort_values('Rank')

        # Determine state
        def derive_status(row):
            rank = row['Rank']
            r_delta = row['Rank_Delta']
            if rank <= top_n:
                return "LEADING"
            elif rank >= len(result_df) - bottom_n + 1:
                return "LAGGING"
            elif r_delta >= 2:
                return "IMPROVING"
            elif r_delta <= -2:
                return "DETERIORATING"
            return "NEUTRAL"
        
        result_df['Status'] = result_df.apply(derive_status, axis=1)

        long_watchlist = result_df[result_df['Rank'] <= top_n]['Name'].tolist()
        short_watchlist = result_df[result_df['Rank'] >= len(result_df) - bottom_n + 1]['Name'].tolist()
        rotation_watchlist = result_df[(result_df['Rank_Delta'] >= 2) & (result_df['Rank'] > top_n)]['Name'].tolist()


        output_data = {
            "sectors": result_df.to_dict('records'),
            "long_watchlist": long_watchlist,
            "short_watchlist": short_watchlist,
            "rotation_watchlist": rotation_watchlist
        }
        
        return output_data

    @staticmethod
    def format_terminal_output(intel_data: Dict[str, Any], legacy_macro_data: List[Dict[str, Any]] = None, breadth: Dict[str, Tuple[int, int]] = None) -> str:
        if not intel_data or "sectors" not in intel_data:
            return ""
            
        legacy_map = {}
        if legacy_macro_data:
            for item in legacy_macro_data:
                legacy_map[item['Ticker']] = item

        lines = []
        lines.append("========================================================================")
        lines.append("              SECTOR INTELLIGENCE ENGINE & WATCHLISTS")
        lines.append("========================================================================")
        lines.append("[1] UNIFIED MACRO & SECTOR INTELLIGENCE RANKINGS")
        
        if breadth and "w" in breadth:
            w_pos, w_neg = breadth["w"]
            m_pos, m_neg = breadth["m"]
            q_pos, q_neg = breadth["q"]
            lines.append(f"    > Sector Breadth  : W (+{w_pos}/-{w_neg}) ; M (+{m_pos}/-{m_neg}) ; Q (+{q_pos}/-{q_neg})\n")
            
        lines.append(f"    {'Rank':<4} {'Sector':<17} {'SPDR'}  {'1-Qtr':>9}  {'YTD':>9}  {'Strength':>9}  {'Rank Δ(1W)':>11}  {'SPY Ex(1M)':>11}  {'Impact':>7}   {'Status'}")
        lines.append("    " + "-" * 111)
        
        for s in intel_data['sectors']:
            rank = int(s['Rank'])
            name = s['Name']
            ticker = s['Ticker']
            p3m = s['3M']
            pytd = s['YTD']
            score = s['Score']
            rank_delta = s['Rank_Delta']
            spy_ex = s['Excess_1M']
            status = s['Status']
            
            p3m_str = f"{p3m:>+8.2f}%" if pd.notna(p3m) else "     ---"
            pytd_str = f"{pytd:>+8.2f}%" if pd.notna(pytd) else "     ---"
            rank_delta_str = f"{int(rank_delta):+d}" if rank_delta != 0 else "-"
            spy_ex_str = f"{spy_ex:>+9.2f}%"
            
            impact = "---"
            if ticker in legacy_map:
                impact = f"{legacy_map[ticker].get('Impact_Mom', 0):>7.1f}"

            lines.append(f"    {rank:<4} {name:<17} {ticker:<4}  {p3m_str:>9}  {pytd_str:>9}  {score:>9.2f}  {rank_delta_str:>11}  {spy_ex_str:>11}  {impact:>7}   {status}")
            
        lines.append("========================================================================\n")
        
        return "\n".join(lines)
