"""Unit tests for utility functions."""

import pytest
import pandas as pd
from datetime import datetime, timedelta
from utils import (
    format_currency,
    format_percentage,
    calculate_trend,
    get_date_range,
    safe_divide,
    truncate_string,
    get_priority_color
)


class TestUtils:
    """Test cases for utility functions."""
    
    def test_format_currency(self):
        """Test currency formatting."""
        assert format_currency(1000.50) == "$1,000.50"
        assert format_currency(0) == "$0.00"
        assert format_currency(1234567.89) == "$1,234,567.89"
    
    def test_format_percentage(self):
        """Test percentage formatting."""
        assert format_percentage(0.1) == "10.0%"
        assert format_percentage(0.555, decimals=2) == "55.50%"
        assert format_percentage(1.0) == "100.0%"
    
    def test_calculate_trend(self):
        """Test trend calculation."""
        # Increasing trend
        series = pd.Series([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        assert calculate_trend(series, window=3) == "increasing"
        
        # Decreasing trend
        series = pd.Series([10, 9, 8, 7, 6, 5, 4, 3, 2, 1])
        assert calculate_trend(series, window=3) == "decreasing"
        
        # Stable trend
        series = pd.Series([5, 5, 5, 5, 5, 5, 5, 5, 5, 5])
        assert calculate_trend(series, window=3) == "stable"
    
    def test_get_date_range(self):
        """Test date range generation."""
        start, end = get_date_range(30)
        
        assert isinstance(start, datetime)
        assert isinstance(end, datetime)
        assert (end - start).days == 29
    
    def test_safe_divide(self):
        """Test safe division."""
        assert safe_divide(10, 2) == 5.0
        assert safe_divide(10, 0) == 0.0
        assert safe_divide(10, 0, default=999) == 999
    
    def test_truncate_string(self):
        """Test string truncation."""
        assert truncate_string("Hello", 10) == "Hello"
        assert truncate_string("Hello World", 8) == "Hello..."
        assert truncate_string("Test", 10, suffix="!") == "Test"
    
    def test_get_priority_color(self):
        """Test priority color mapping."""
        assert get_priority_color("High") == "#ff4b4b"
        assert get_priority_color("高") == "#ff4b4b"
        assert get_priority_color("Medium") == "#ffa724"
        assert get_priority_color("中") == "#ffa724"
        assert get_priority_color("Low") == "#00cc88"
        assert get_priority_color("低") == "#00cc88"
        assert get_priority_color("Unknown") == "#808080"