"""Main orchestrator for analytics data pipeline.

This module coordinates the data ingestion, KPI calculation, and insight generation
processes.
"""

import os
import sys
from datetime import datetime

from dotenv import load_dotenv
from loguru import logger

from ai_insight import extract_tweets_from_insights, generate_insights, post_tweet
from data_ingest import (
    create_kpi_datamart,
    fetch_ga_df,
    fetch_stripe_df,
    save_kpi_data,
)

# Configure logger
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
)
logger.add(
    "./output/analytics_pipeline.log",
    rotation="1 day",
    retention="7 days",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
)


def run_pipeline():
    """Run the complete analytics pipeline."""
    logger.info("Starting analytics pipeline")
    
    try:
        # Load environment variables
        load_dotenv()
        
        # Create output directory
        os.makedirs("./output", exist_ok=True)
        
        # Step 1: Fetch data from GA4
        logger.info("Step 1: Fetching GA4 data")
        ga_df = fetch_ga_df()
        logger.success(f"Fetched {len(ga_df)} days of GA4 data")
        
        # Step 2: Fetch data from Stripe
        logger.info("Step 2: Fetching Stripe data")
        stripe_df = fetch_stripe_df()
        logger.success(f"Fetched {len(stripe_df)} days of Stripe data")
        
        # Step 3: Create KPI datamart
        logger.info("Step 3: Creating KPI datamart")
        kpi_df = create_kpi_datamart(ga_df, stripe_df)
        logger.success(f"Created KPI datamart with {len(kpi_df)} rows")
        
        # Step 4: Save KPI data
        logger.info("Step 4: Saving KPI data")
        save_kpi_data(kpi_df)
        logger.success("Saved KPI data to output/kpi_daily.csv")
        
        # Step 5: Generate AI insights
        logger.info("Step 5: Generating AI insights")
        insights_md, action_df = generate_insights(kpi_df)
        logger.success("Generated AI insights and action plan")
        
        # Step 6: Optional - Post tweet
        if os.getenv("TW_BEARER_TOKEN"):
            logger.info("Step 6: Attempting to post tweet")
            tweets = extract_tweets_from_insights(insights_md)
            if tweets:
                # Post the first tweet
                if post_tweet(tweets[0]):
                    logger.success("Posted tweet successfully")
                else:
                    logger.warning("Failed to post tweet")
            else:
                logger.warning("No tweets found in insights")
        else:
            logger.info("Step 6: Twitter bearer token not found, skipping tweet")
        
        # Summary
        logger.info("=" * 50)
        logger.success("Analytics pipeline completed successfully!")
        logger.info(f"Total sessions: {kpi_df['sessions'].sum():.0f}")
        logger.info(f"Total revenue: ${kpi_df['gross_revenue'].sum():.2f}")
        logger.info(f"Average conversion rate: {kpi_df['conversion_rate'].mean():.2%}")
        logger.info(f"Generated {len(action_df)} action items")
        logger.info("=" * 50)
        
        return True
        
    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}")
        logger.exception(e)
        return False


def main():
    """Main entry point."""
    start_time = datetime.now()
    
    logger.info(f"Analytics Pipeline Started at {start_time}")
    
    success = run_pipeline()
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    logger.info(f"Pipeline completed in {duration:.2f} seconds")
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()