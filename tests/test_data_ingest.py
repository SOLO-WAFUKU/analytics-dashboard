"""Unit tests for data ingestion module."""

import pytest
import pandas as pd
from unittest.mock import MagicMock, patch
from data_ingest import (
    fetch_ga_df,
    fetch_stripe_df,
    create_kpi_datamart,
    save_kpi_data
)


class TestDataIngest:
    """Test cases for data ingestion functions."""
    
    @patch('data_ingest.BetaAnalyticsDataClient')
    def test_fetch_ga_df(self, mock_client):
        """Test Google Analytics data fetching."""
        # Setup mock
        mock_response = MagicMock()
        mock_response.rows = []
        mock_client.return_value.run_report.return_value = mock_response
        
        # Test
        with patch('os.getenv', return_value='123456'):
            df = fetch_ga_df()
        
        assert isinstance(df, pd.DataFrame)
        assert all(col in df.columns for col in ['date', 'sessions', 'newUsers', 'totalRevenue', 'transactions'])
    
    @patch('stripe.PaymentIntent')
    def test_fetch_stripe_df(self, mock_pi):
        """Test Stripe data fetching."""
        # Setup mock
        mock_pi.list.return_value.data = []
        mock_pi.list.return_value.has_more = False
        
        # Test
        with patch('os.getenv', return_value='sk_test_123'):
            df = fetch_stripe_df()
        
        assert isinstance(df, pd.DataFrame)
        assert all(col in df.columns for col in ['date', 'gross_revenue'])
    
    def test_create_kpi_datamart(self):
        """Test KPI datamart creation."""
        # Create sample data
        ga_df = pd.DataFrame({
            'date': pd.date_range('2024-01-01', periods=5),
            'sessions': [100, 150, 200, 250, 300],
            'newUsers': [50, 75, 100, 125, 150],
            'totalRevenue': [1000, 1500, 2000, 2500, 3000],
            'transactions': [10, 15, 20, 25, 30]
        })
        
        stripe_df = pd.DataFrame({
            'date': pd.date_range('2024-01-01', periods=5),
            'gross_revenue': [1100, 1600, 2100, 2600, 3100]
        })
        
        # Test
        kpi_df = create_kpi_datamart(ga_df, stripe_df)
        
        assert isinstance(kpi_df, pd.DataFrame)
        assert 'conversion_rate' in kpi_df.columns
        assert 'revenue_per_session' in kpi_df.columns
        assert 'ltv_cac_ratio' in kpi_df.columns
        assert len(kpi_df) == 5