"""AI-powered insights generation module.

This module uses OpenAI's GPT-4 to analyze KPI data and generate actionable insights
and social media content.
"""

import json
import os
import re
from typing import Dict, List, Tuple

import openai
import pandas as pd
import tweepy
from dotenv import load_dotenv
from loguru import logger

load_dotenv()


def generate_insights(df: pd.DataFrame) -> Tuple[str, pd.DataFrame]:
    """Generate AI-powered insights from KPI data.
    
    Args:
        df: DataFrame with KPI data
    
    Returns:
        Tuple[str, pd.DataFrame]: Markdown insights and action plan DataFrame
    """
    try:
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        client = openai.OpenAI(api_key=openai_api_key)
        
        # Calculate summary statistics
        summary = {
            "sessions": {
                "mean": df["sessions"].mean(),
                "max": df["sessions"].max(),
                "min": df["sessions"].min(),
                "trend": "increasing" if df["sessions"].iloc[-7:].mean() > df["sessions"].iloc[:7].mean() else "decreasing"
            },
            "newUsers": {
                "mean": df["newUsers"].mean(),
                "max": df["newUsers"].max(),
                "min": df["newUsers"].min(),
                "trend": "increasing" if df["newUsers"].iloc[-7:].mean() > df["newUsers"].iloc[:7].mean() else "decreasing"
            },
            "gross_revenue": {
                "mean": df["gross_revenue"].mean(),
                "max": df["gross_revenue"].max(),
                "min": df["gross_revenue"].min(),
                "total": df["gross_revenue"].sum(),
                "trend": "increasing" if df["gross_revenue"].iloc[-7:].mean() > df["gross_revenue"].iloc[:7].mean() else "decreasing"
            },
            "conversion_rate": {
                "mean": df["conversion_rate"].mean(),
                "max": df["conversion_rate"].max(),
                "min": df["conversion_rate"].min(),
                "trend": "increasing" if df["conversion_rate"].iloc[-7:].mean() > df["conversion_rate"].iloc[:7].mean() else "decreasing"
            },
            "revenue_per_session": {
                "mean": df["revenue_per_session"].mean(),
                "max": df["revenue_per_session"].max(),
                "min": df["revenue_per_session"].min(),
                "trend": "increasing" if df["revenue_per_session"].iloc[-7:].mean() > df["revenue_per_session"].iloc[:7].mean() else "decreasing"
            }
        }
        
        # Create prompt
        prompt = f"""以下は直近30日間のKPIサマリーです：

セッション数:
- 平均: {summary['sessions']['mean']:.1f}
- 最大: {summary['sessions']['max']:.1f}
- 最小: {summary['sessions']['min']:.1f}
- トレンド: {summary['sessions']['trend']}

新規ユーザー:
- 平均: {summary['newUsers']['mean']:.1f}
- 最大: {summary['newUsers']['max']:.1f}
- 最小: {summary['newUsers']['min']:.1f}
- トレンド: {summary['newUsers']['trend']}

売上高:
- 平均: ${summary['gross_revenue']['mean']:.2f}
- 最大: ${summary['gross_revenue']['max']:.2f}
- 最小: ${summary['gross_revenue']['min']:.2f}
- 合計: ${summary['gross_revenue']['total']:.2f}
- トレンド: {summary['gross_revenue']['trend']}

コンバージョン率:
- 平均: {summary['conversion_rate']['mean']:.2%}
- 最大: {summary['conversion_rate']['max']:.2%}
- 最小: {summary['conversion_rate']['min']:.2%}
- トレンド: {summary['conversion_rate']['trend']}

セッションあたり収益:
- 平均: ${summary['revenue_per_session']['mean']:.2f}
- 最大: ${summary['revenue_per_session']['max']:.2f}
- 最小: ${summary['revenue_per_session']['min']:.2f}
- トレンド: {summary['revenue_per_session']['trend']}

以下の形式で回答してください：

1. 改善すべきポイントを最大5件列挙（Markdown表形式）
| priority | issue | recommended_action |
|----------|-------|-------------------|
| 高 | [40字以内の問題点] | [80字以内の改善アクション] |
| 中 | [40字以内の問題点] | [80字以内の改善アクション] |
| 低 | [40字以内の問題点] | [80字以内の改善アクション] |

2. X/Twitter投稿文（2本、各140字以内、絵文字1つ、CTA付き）"""

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "あなたはデータ分析とマーケティングの専門家です。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        response_text = response.choices[0].message.content
        
        # Parse response
        insight_md, action_df = parse_gpt_response(response_text)
        
        # Save outputs
        save_insights(insight_md, action_df)
        
        logger.info("Generated AI insights successfully")
        return insight_md, action_df
        
    except Exception as e:
        logger.error(f"Error generating insights: {str(e)}")
        # Return fallback data
        fallback_md = "# AI Insights\n\nError generating insights. Please check your OpenAI API key."
        fallback_df = pd.DataFrame({
            "priority": ["High"],
            "issue": ["AI insight generation failed"],
            "recommended_action": ["Check OpenAI API key and retry"]
        })
        return fallback_md, fallback_df


def parse_gpt_response(response_text: str) -> Tuple[str, pd.DataFrame]:
    """Parse GPT response into markdown and DataFrame.
    
    Args:
        response_text: Raw GPT response text
    
    Returns:
        Tuple[str, pd.DataFrame]: Parsed markdown and action plan DataFrame
    """
    try:
        # Extract table data
        table_pattern = r'\| (\w+) \| ([^|]+) \| ([^|]+) \|'
        matches = re.findall(table_pattern, response_text)
        
        action_data = []
        for match in matches:
            priority, issue, action = match
            priority = priority.strip()
            if priority in ["高", "中", "低"]:
                action_data.append({
                    "priority": priority,
                    "issue": issue.strip(),
                    "recommended_action": action.strip()
                })
        
        # If no data found, create default
        if not action_data:
            action_data = [
                {
                    "priority": "高",
                    "issue": "データ分析結果の解析が必要",
                    "recommended_action": "KPIの詳細分析を実施し、具体的な改善点を特定する"
                }
            ]
        
        action_df = pd.DataFrame(action_data)
        
        # Create markdown with full response
        insight_md = f"""# AI-Powered Insights

## KPI Analysis

{response_text}

## Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        return insight_md, action_df
        
    except Exception as e:
        logger.error(f"Error parsing GPT response: {str(e)}")
        raise


def save_insights(insight_md: str, action_df: pd.DataFrame) -> None:
    """Save insights to files.
    
    Args:
        insight_md: Markdown insights
        action_df: Action plan DataFrame
    """
    try:
        os.makedirs("./output", exist_ok=True)
        
        # Save markdown
        with open("./output/insights.md", "w", encoding="utf-8") as f:
            f.write(insight_md)
        
        # Save action plan CSV
        action_df.to_csv("./output/action_plan.csv", index=False, encoding="utf-8")
        
        logger.info("Saved insights to output files")
        
    except Exception as e:
        logger.error(f"Error saving insights: {str(e)}")
        raise


def post_tweet(tweet_text: str) -> bool:
    """Post a tweet using Twitter API v2.
    
    Args:
        tweet_text: Text to tweet
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        bearer_token = os.getenv("TW_BEARER_TOKEN")
        if not bearer_token:
            logger.info("Twitter bearer token not found, skipping tweet")
            return False
        
        # Create Twitter client
        client = tweepy.Client(bearer_token=bearer_token)
        
        # Post tweet
        response = client.create_tweet(text=tweet_text)
        
        logger.info(f"Posted tweet successfully: {response.data['id']}")
        return True
        
    except Exception as e:
        logger.error(f"Error posting tweet: {str(e)}")
        return False


def extract_tweets_from_insights(insight_md: str) -> List[str]:
    """Extract tweet texts from insights markdown.
    
    Args:
        insight_md: Markdown insights containing tweets
    
    Returns:
        List[str]: List of tweet texts
    """
    try:
        # Look for tweet patterns in the markdown
        tweet_pattern = r'(?:Tweet|ツイート|投稿)[:\s]*["\']?([^"\'\n]{1,280})["\']?'
        tweets = re.findall(tweet_pattern, insight_md, re.MULTILINE | re.IGNORECASE)
        
        # Clean and filter tweets
        cleaned_tweets = []
        for tweet in tweets:
            tweet = tweet.strip()
            if 10 < len(tweet) <= 280:  # Valid tweet length
                cleaned_tweets.append(tweet)
        
        return cleaned_tweets[:2]  # Return max 2 tweets
        
    except Exception as e:
        logger.error(f"Error extracting tweets: {str(e)}")
        return []