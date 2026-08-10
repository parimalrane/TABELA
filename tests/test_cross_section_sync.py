import pytest
import pandas as pd
from unittest.mock import patch
from core.pipeline import build_candidates
from engines import breadth_engine

def mock_build_theme_breadth(stocks, long_candidates):
    # Intentional stale rendering: adding 'GHOST_TICKER' that doesn't exist in long_candidates
    return pd.DataFrame({
        "Mapped_Theme": ["Test Theme"],
        "Leaders": ["GHOST_TICKER"]
    })

def test_fail_build_on_desync(mocker):
    # Dummy inputs
    stocks = pd.DataFrame({
        "Ticker": ["A", "B"],
        "Industry": ["Tech", "Tech"],
        "Sector": ["Tech", "Tech"],
        "Mapped_Theme": ["Test Theme", "Test Theme"],
        "ETF_Theme": ["Test Theme", "Test Theme"],
        "RS_Rating": [90, 80],
        "Composite_Score": [90, 80],
        "Sales_Score": [80, 80],
        "Zacks_Score": [80, 80],
        "Is_Long_Candidate": [False, False],
        "Tracking_State": ["N/A", "N/A"]
    })
    
    # Mock registry loaders so it doesn't try to read real files
    mocker.patch('core.pipeline.load_registry', return_value={})
    mocker.patch('core.pipeline.pre_distribution_update', return_value=({}, set()))
    mocker.patch('core.pipeline.post_distribution_update', return_value={})
    
    # Inject our stale breadth module
    mocker.patch('core.pipeline.build_theme_breadth', side_effect=mock_build_theme_breadth)
    
    # Run and assert ValueError
    with pytest.raises(ValueError) as excinfo:
        build_candidates(stocks)
        
    assert "Build validation failed" in str(excinfo.value)
    assert "GHOST_TICKER" in str(excinfo.value)
