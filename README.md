# Analytics Dashboard

A comprehensive analytics dashboard that integrates Google Analytics 4 and Stripe data, provides AI-powered insights, and features an interactive Streamlit interface.

## Features

- **Data Integration**: Fetches last 30 days of data from GA4 and Stripe
- **KPI Calculation**: Computes conversion rate, revenue per session, and other key metrics
- **AI Insights**: GPT-4 powered analysis with actionable recommendations
- **Interactive Dashboard**: Streamlit app with visualizations and real-time updates
- **Automated Pipeline**: GitHub Actions workflow for daily execution
- **Social Media Integration**: Optional Twitter/X posting of insights

## Quick Start

### Prerequisites

- Python 3.11+
- Google Analytics 4 property with API access
- Stripe account with API key
- OpenAI API key for GPT-4
- (Optional) Twitter/X Bearer Token for auto-posting

### Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd analytics-dashboard
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your actual credentials:
# GA_PROPERTY_ID=your_ga_property_id
# STRIPE_API_KEY=sk_live_your_stripe_key
# OPENAI_API_KEY=sk-your_openai_key
# TW_BEARER_TOKEN=your_twitter_bearer_token  # Optional
```

### Running the Application

#### Run the data pipeline:
```bash
python main.py
```

This will:
1. Fetch data from GA4 and Stripe
2. Create KPI datamart
3. Generate AI insights
4. Save results to `./output/`

#### Launch the dashboard:
```bash
streamlit run app.py
```

Open http://localhost:8501 in your browser.

## Project Structure

```
analytics-dashboard/
├── app.py              # Streamlit dashboard application
├── main.py             # Pipeline orchestrator
├── data_ingest.py      # GA4 and Stripe data fetching
├── ai_insight.py       # GPT-4 powered insights generation
├── utils.py            # Utility functions
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variables template
├── output/             # Generated data and insights
│   ├── kpi_daily.csv
│   ├── insights.md
│   └── action_plan.csv
├── tests/              # Unit test stubs
│   ├── test_data_ingest.py
│   ├── test_ai_insight.py
│   └── test_utils.py
└── .github/
    └── workflows/
        └── daily.yml   # GitHub Actions workflow

```

## Dashboard Features

### Overview Tab
- 30-day KPI summary with trend indicators
- Interactive matplotlib charts for:
  - Daily sessions
  - Revenue trends
  - Conversion rates
  - Revenue per session
- Statistical summary table

### Action Plan Tab
- AI-generated recommendations with priority levels
- Color-coded action items (High=Red, Medium=Yellow, Low=Green)
- "Regenerate Suggestions" button for fresh insights
- Full markdown analysis display

### Raw Data Tab
- Complete KPI datamart view
- CSV download functionality
- Data range information

## Automated Execution

The GitHub Actions workflow runs daily at 04:00 JST:

1. Set up repository secrets:
   - `GA_PROPERTY_ID`
   - `STRIPE_API_KEY`
   - `OPENAI_API_KEY`
   - `TW_BEARER_TOKEN` (optional)

2. The workflow will:
   - Execute the pipeline
   - Save artifacts for 30 days
   - Post to Twitter/X if configured

## KPI Definitions

- **Sessions**: Total user sessions from GA4
- **New Users**: First-time visitors
- **Gross Revenue**: Total succeeded payments from Stripe
- **Conversion Rate**: Transactions / Sessions
- **Revenue per Session**: Gross Revenue / Sessions
- **LTV/CAC Ratio**: Currently placeholder (NaN)

## Development

### Running Tests
```bash
pytest tests/
```

### Adding New KPIs
1. Update `data_ingest.py` to fetch new metrics
2. Modify `create_kpi_datamart()` to calculate KPIs
3. Update dashboard visualizations in `app.py`

### Customizing AI Insights
Edit the prompt in `ai_insight.py:generate_insights()` to modify:
- Analysis focus areas
- Recommendation format
- Tweet content style

## Troubleshooting

### Common Issues

1. **Google Analytics API Error**
   - Verify GA_PROPERTY_ID format (numeric only)
   - Check API credentials and permissions

2. **Stripe API Error**
   - Ensure API key has read permissions
   - Check date range for available data

3. **OpenAI API Error**
   - Verify API key and available credits
   - Check model availability (gpt-4)

4. **Dashboard Not Loading**
   - Run data pipeline first: `python main.py`
   - Check `./output/` directory exists

## Security Notes

- Never commit `.env` file
- Use GitHub Secrets for CI/CD
- Rotate API keys regularly
- Review AI-generated content before posting

## License

This project is provided as-is for demonstration purposes.