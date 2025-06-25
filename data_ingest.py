"""Data ingestion module for GA4 and Stripe data.

This module provides functions to fetch data from Google Analytics 4 and Stripe,
processing them into pandas DataFrames for further analysis.
"""

import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import pandas as pd
import stripe
from dotenv import load_dotenv
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
)
from loguru import logger

load_dotenv()


def fetch_ga_df() -> pd.DataFrame:
    """Fetch Google Analytics 4 data for the last 30 days.
    
    Returns:
        pd.DataFrame: DataFrame with columns: date, sessions, newUsers, 
                     totalRevenue, transactions
    
    Raises:
        Exception: If GA4 API call fails
    """
    try:
        property_id = os.getenv("GA_PROPERTY_ID")
        if not property_id:
            raise ValueError("GA_PROPERTY_ID not found in environment variables")
        
        client = BetaAnalyticsDataClient()
        
        # Calculate date range (last 30 days)
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=29)
        
        request = RunReportRequest(
            property=f"properties/{property_id}",
            dimensions=[Dimension(name="date")],
            metrics=[
                Metric(name="sessions"),
                Metric(name="newUsers"),
                Metric(name="totalRevenue"),
                Metric(name="transactions"),
            ],
            date_ranges=[DateRange(
                start_date=start_date.strftime("%Y-%m-%d"),
                end_date=end_date.strftime("%Y-%m-%d")
            )],
        )
        
        response = client.run_report(request)
        
        # Convert response to DataFrame
        data = []
        for row in response.rows:
            data.append({
                "date": row.dimension_values[0].value,
                "sessions": float(row.metric_values[0].value),
                "newUsers": float(row.metric_values[1].value),
                "totalRevenue": float(row.metric_values[2].value),
                "transactions": float(row.metric_values[3].value),
            })
        
        df = pd.DataFrame(data)
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date")
        
        logger.info(f"Fetched GA4 data: {len(df)} days")
        return df
        
    except Exception as e:
        logger.error(f"Error fetching GA4 data: {str(e)}")
        raise


def fetch_stripe_df() -> pd.DataFrame:
    """Fetch Stripe payment data for the last 30 days.
    
    Returns:
        pd.DataFrame: DataFrame with columns: date, gross_revenue
    
    Raises:
        Exception: If Stripe API call fails
    """
    try:
        stripe_api_key = os.getenv("STRIPE_API_KEY")
        if not stripe_api_key:
            raise ValueError("STRIPE_API_KEY not found in environment variables")
        
        stripe.api_key = stripe_api_key
        
        # Calculate date range (last 30 days)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=29)
        
        # Fetch all succeeded payment intents
        payment_intents = []
        has_more = True
        starting_after = None
        
        while has_more:
            params = {
                "limit": 100,
                "status": "succeeded",
                "created": {
                    "gte": int(start_date.timestamp()),
                    "lte": int(end_date.timestamp()),
                },
            }
            if starting_after:
                params["starting_after"] = starting_after
            
            response = stripe.PaymentIntent.list(**params)
            payment_intents.extend(response.data)
            has_more = response.has_more
            if has_more:
                starting_after = response.data[-1].id
        
        # Aggregate by date
        daily_revenue = {}
        for pi in payment_intents:
            date = datetime.fromtimestamp(pi.created).date()
            amount = pi.amount / 100.0  # Convert from cents to dollars
            
            if date not in daily_revenue:
                daily_revenue[date] = 0
            daily_revenue[date] += amount
        
        # Create DataFrame with all dates in range
        date_range = pd.date_range(start=start_date.date(), end=end_date.date(), freq='D')
        df = pd.DataFrame({
            "date": date_range,
            "gross_revenue": [daily_revenue.get(d.date(), 0.0) for d in date_range]
        })
        
        logger.info(f"Fetched Stripe data: {len(df)} days, total revenue: ${df['gross_revenue'].sum():.2f}")
        return df
        
    except Exception as e:
        logger.error(f"Error fetching Stripe data: {str(e)}")
        raise


def create_kpi_datamart(ga_df: pd.DataFrame, stripe_df: pd.DataFrame) -> pd.DataFrame:
    """Create KPI datamart by joining GA and Stripe data.
    
    Args:
        ga_df: Google Analytics DataFrame
        stripe_df: Stripe DataFrame
    
    Returns:
        pd.DataFrame: KPI datamart with calculated metrics
    """
    try:
        # Left join on date
        kpi_df = ga_df.merge(stripe_df, on="date", how="left")
        
        # Calculate KPIs with 4 decimal precision
        kpi_df["conversion_rate"] = (
            kpi_df["transactions"] / kpi_df["sessions"]
        ).round(4)
        
        kpi_df["revenue_per_session"] = (
            kpi_df["gross_revenue"] / kpi_df["sessions"]
        ).round(4)
        
        # Placeholder for LTV/CAC ratio
        kpi_df["ltv_cac_ratio"] = float("nan")
        
        # Ensure all numeric columns are float with 4 decimals
        numeric_cols = ["sessions", "newUsers", "totalRevenue", "transactions", 
                       "gross_revenue", "conversion_rate", "revenue_per_session"]
        for col in numeric_cols:
            kpi_df[col] = kpi_df[col].astype(float).round(4)
        
        logger.info(f"Created KPI datamart with {len(kpi_df)} rows")
        return kpi_df
        
    except Exception as e:
        logger.error(f"Error creating KPI datamart: {str(e)}")
        raise


def save_kpi_data(kpi_df: pd.DataFrame, output_path: str = "./output/kpi_daily.csv") -> None:
    """Save KPI datamart to CSV file.
    
    Args:
        kpi_df: KPI DataFrame to save
        output_path: Path to output CSV file
    """
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        kpi_df.to_csv(output_path, index=False, float_format="%.4f")
        logger.info(f"Saved KPI data to {output_path}")
    except Exception as e:
        logger.error(f"Error saving KPI data: {str(e)}")
        raise