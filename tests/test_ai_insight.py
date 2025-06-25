"""Unit tests for AI insights module."""

import pytest
import pandas as pd
from unittest.mock import MagicMock, patch
from ai_insight import (
    generate_insights,
    parse_gpt_response,
    extract_tweets_from_insights
)


class TestAIInsight:
    """Test cases for AI insight functions."""
    
    @patch('openai.OpenAI')
    def test_generate_insights(self, mock_openai):
        """Test AI insight generation."""
        # Setup mock
        mock_response = MagicMock()
        mock_response.choices[0].message.content = """| 高 | Test issue | Test action |
        
        Tweet: Test tweet with emoji 🚀 and CTA"""
        mock_openai.return_value.chat.completions.create.return_value = mock_response
        
        # Create sample data
        df = pd.DataFrame({
            'date': pd.date_range('2024-01-01', periods=5),
            'sessions': [100, 150, 200, 250, 300],
            'newUsers': [50, 75, 100, 125, 150],
            'gross_revenue': [1000, 1500, 2000, 2500, 3000],
            'conversion_rate': [0.1, 0.1, 0.1, 0.1, 0.1],
            'revenue_per_session': [10, 10, 10, 10, 10]
        })
        
        # Test
        with patch('os.getenv', return_value='sk-test123'):
            insights_md, action_df = generate_insights(df)
        
        assert isinstance(insights_md, str)
        assert isinstance(action_df, pd.DataFrame)
        assert len(action_df) > 0
    
    def test_parse_gpt_response(self):
        """Test GPT response parsing."""
        response_text = """| 高 | Performance issue | Optimize database queries |
| 中 | UX problem | Redesign checkout flow |
| 低 | Minor bug | Fix tooltip display |

Tweet 1: Amazing results this month! 🚀
Tweet 2: Check out our new features! 💡"""
        
        insights_md, action_df = parse_gpt_response(response_text)
        
        assert isinstance(insights_md, str)
        assert isinstance(action_df, pd.DataFrame)
        assert len(action_df) == 3
        assert all(col in action_df.columns for col in ['priority', 'issue', 'recommended_action'])
    
    def test_extract_tweets_from_insights(self):
        """Test tweet extraction from insights."""
        insights_md = """# Insights
        
Tweet: Check out our amazing results this month! 🚀 Visit our site for more.
Tweet: New features just launched! 💡 Try them today.
Some other content here."""
        
        tweets = extract_tweets_from_insights(insights_md)
        
        assert isinstance(tweets, list)
        assert len(tweets) <= 2
        assert all(len(tweet) <= 280 for tweet in tweets)