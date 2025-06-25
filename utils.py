"""Utility functions for analytics dashboard.

This module provides common utility functions used across the application.
"""

import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import pandas as pd
from loguru import logger


def ensure_output_dir(path: str = "./output") -> None:
    """Ensure output directory exists.
    
    Args:
        path: Path to output directory
    """
    os.makedirs(path, exist_ok=True)
    logger.debug(f"Ensured output directory exists: {path}")


def format_currency(value: float, currency: str = "$") -> str:
    """Format value as currency string.
    
    Args:
        value: Numeric value to format
        currency: Currency symbol
    
    Returns:
        str: Formatted currency string
    """
    return f"{currency}{value:,.2f}"


def format_percentage(value: float, decimals: int = 1) -> str:
    """Format value as percentage string.
    
    Args:
        value: Numeric value (0.1 = 10%)
        decimals: Number of decimal places
    
    Returns:
        str: Formatted percentage string
    """
    return f"{value * 100:.{decimals}f}%"


def calculate_trend(series: pd.Series, window: int = 7) -> str:
    """Calculate trend direction from time series data.
    
    Args:
        series: Pandas series with time series data
        window: Window size for comparison
    
    Returns:
        str: "increasing", "decreasing", or "stable"
    """
    if len(series) < window * 2:
        return "insufficient_data"
    
    recent_mean = series.iloc[-window:].mean()
    past_mean = series.iloc[:window].mean()
    
    if past_mean == 0:
        return "stable"
    
    change_pct = (recent_mean - past_mean) / past_mean
    
    if change_pct > 0.05:
        return "increasing"
    elif change_pct < -0.05:
        return "decreasing"
    else:
        return "stable"


def get_date_range(days: int = 30) -> tuple[datetime, datetime]:
    """Get date range for data fetching.
    
    Args:
        days: Number of days to look back
    
    Returns:
        tuple: (start_date, end_date)
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days-1)
    return start_date, end_date


def validate_env_vars(required_vars: List[str]) -> Dict[str, bool]:
    """Validate required environment variables.
    
    Args:
        required_vars: List of required environment variable names
    
    Returns:
        Dict[str, bool]: Dictionary of var_name: is_present
    """
    results = {}
    for var in required_vars:
        results[var] = bool(os.getenv(var))
        if not results[var]:
            logger.warning(f"Missing environment variable: {var}")
    return results


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safely divide two numbers, returning default if denominator is zero.
    
    Args:
        numerator: The numerator
        denominator: The denominator
        default: Default value if division by zero
    
    Returns:
        float: Result of division or default
    """
    if denominator == 0:
        return default
    return numerator / denominator


def truncate_string(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate string to maximum length.
    
    Args:
        text: String to truncate
        max_length: Maximum allowed length
        suffix: Suffix to append if truncated
    
    Returns:
        str: Truncated string
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def get_priority_color(priority: str) -> str:
    """Get color code for priority level.
    
    Args:
        priority: Priority level (High/Medium/Low or 高/中/低)
    
    Returns:
        str: Hex color code
    """
    color_map = {
        "High": "#ff4b4b",
        "高": "#ff4b4b",
        "Medium": "#ffa724",
        "中": "#ffa724",
        "Low": "#00cc88",
        "低": "#00cc88",
    }
    return color_map.get(priority, "#808080")


def parse_date_string(date_str: str) -> Optional[datetime]:
    """Parse various date string formats.
    
    Args:
        date_str: Date string to parse
    
    Returns:
        Optional[datetime]: Parsed datetime or None
    """
    formats = [
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%Y%m%d",
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    logger.warning(f"Could not parse date string: {date_str}")
    return None