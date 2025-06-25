"""Streamlit dashboard application for analytics insights.

This module provides an interactive dashboard with KPI visualizations,
AI-powered insights, and raw data views.
"""

import os
from datetime import datetime

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from loguru import logger

from ai_insight import generate_insights
from auth import check_password, logout, get_login_status
from config_manager import (
    get_credential_status,
    load_credentials,
    save_credentials,
    validate_credentials,
)
from data_ingest import (
    create_kpi_datamart,
    fetch_ga_df,
    fetch_stripe_df,
    save_kpi_data,
)


def load_kpi_data() -> pd.DataFrame:
    """Load KPI data from CSV file.
    
    Returns:
        pd.DataFrame: KPI data
    """
    try:
        if os.path.exists("./output/kpi_daily.csv"):
            df = pd.read_csv("./output/kpi_daily.csv")
            df["date"] = pd.to_datetime(df["date"])
            return df
        else:
            st.error("KPI data not found. Please run data ingestion first.")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading KPI data: {str(e)}")
        return pd.DataFrame()


def load_insights() -> tuple:
    """Load insights and action plan from files.
    
    Returns:
        tuple: (insights_md, action_df)
    """
    try:
        insights_md = ""
        action_df = pd.DataFrame()
        
        if os.path.exists("./output/insights.md"):
            with open("./output/insights.md", "r", encoding="utf-8") as f:
                insights_md = f.read()
        
        if os.path.exists("./output/action_plan.csv"):
            action_df = pd.read_csv("./output/action_plan.csv")
        
        return insights_md, action_df
    except Exception as e:
        st.error(f"Error loading insights: {str(e)}")
        return "", pd.DataFrame()


def plot_kpi_metric(df: pd.DataFrame, metric: str, title: str, ylabel: str, format_func=None):
    """Plot a single KPI metric over time.
    
    Args:
        df: DataFrame with KPI data
        metric: Column name to plot
        title: Plot title
        ylabel: Y-axis label
        format_func: Optional function to format values
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Plot line
    ax.plot(df["date"], df[metric], marker="o", markersize=4, linewidth=2)
    
    # Add trend line
    z = np.polyfit(range(len(df)), df[metric], 1)
    p = np.poly1d(z)
    ax.plot(df["date"], p(range(len(df))), "--", alpha=0.5, label="Trend")
    
    # Formatting
    ax.set_title(title, fontsize=16, fontweight="bold", pad=20)
    ax.set_xlabel("Date", fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)
    ax.grid(True, alpha=0.3)
    ax.legend()
    
    # Format y-axis
    if format_func:
        ax.yaxis.set_major_formatter(plt.FuncFormatter(format_func))
    
    # Rotate x-axis labels
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    return fig


def render_overview_tab(df: pd.DataFrame):
    """Render the Overview tab with KPI visualizations."""
    st.header("KPI Overview")
    
    if df.empty:
        st.warning("No data available to display.")
        return
    
    # Summary statistics
    st.subheader("30-Day Summary")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "Avg Sessions",
            f"{df['sessions'].mean():.0f}",
            f"{((df['sessions'].iloc[-7:].mean() / df['sessions'].iloc[:7].mean() - 1) * 100):.1f}%"
        )
    
    with col2:
        st.metric(
            "Avg New Users",
            f"{df['newUsers'].mean():.0f}",
            f"{((df['newUsers'].iloc[-7:].mean() / df['newUsers'].iloc[:7].mean() - 1) * 100):.1f}%"
        )
    
    with col3:
        st.metric(
            "Total Revenue",
            f"${df['gross_revenue'].sum():,.2f}",
            f"{((df['gross_revenue'].iloc[-7:].sum() / df['gross_revenue'].iloc[:7].sum() - 1) * 100):.1f}%"
        )
    
    with col4:
        st.metric(
            "Avg Conv. Rate",
            f"{df['conversion_rate'].mean():.2%}",
            f"{(df['conversion_rate'].iloc[-7:].mean() - df['conversion_rate'].iloc[:7].mean()) * 100:.2f}pp"
        )
    
    with col5:
        st.metric(
            "Avg Rev/Session",
            f"${df['revenue_per_session'].mean():.2f}",
            f"{((df['revenue_per_session'].iloc[-7:].mean() / df['revenue_per_session'].iloc[:7].mean() - 1) * 100):.1f}%"
        )
    
    # Visualizations
    st.subheader("Trend Analysis")
    
    # Sessions plot
    fig1 = plot_kpi_metric(df, "sessions", "Daily Sessions", "Sessions")
    st.pyplot(fig1)
    
    # Revenue plot
    fig2 = plot_kpi_metric(
        df, "gross_revenue", "Daily Revenue", "Revenue ($)",
        format_func=lambda x, p: f"${x:,.0f}"
    )
    st.pyplot(fig2)
    
    # Conversion rate plot
    fig3 = plot_kpi_metric(
        df, "conversion_rate", "Conversion Rate", "Rate (%)",
        format_func=lambda x, p: f"{x:.1%}"
    )
    st.pyplot(fig3)
    
    # Revenue per session plot
    fig4 = plot_kpi_metric(
        df, "revenue_per_session", "Revenue per Session", "Revenue ($)",
        format_func=lambda x, p: f"${x:.2f}"
    )
    st.pyplot(fig4)
    
    # Summary table
    st.subheader("Statistical Summary")
    
    summary_data = {
        "Metric": ["Sessions", "New Users", "Revenue", "Conversion Rate", "Rev/Session"],
        "Mean": [
            f"{df['sessions'].mean():.1f}",
            f"{df['newUsers'].mean():.1f}",
            f"${df['gross_revenue'].mean():.2f}",
            f"{df['conversion_rate'].mean():.2%}",
            f"${df['revenue_per_session'].mean():.2f}"
        ],
        "Max": [
            f"{df['sessions'].max():.0f}",
            f"{df['newUsers'].max():.0f}",
            f"${df['gross_revenue'].max():.2f}",
            f"{df['conversion_rate'].max():.2%}",
            f"${df['revenue_per_session'].max():.2f}"
        ],
        "Min": [
            f"{df['sessions'].min():.0f}",
            f"{df['newUsers'].min():.0f}",
            f"${df['gross_revenue'].min():.2f}",
            f"{df['conversion_rate'].min():.2%}",
            f"${df['revenue_per_session'].min():.2f}"
        ]
    }
    
    st.table(pd.DataFrame(summary_data))


def render_action_plan_tab(df: pd.DataFrame):
    """Render the Action Plan tab with AI-generated insights."""
    st.header("AI-Powered Action Plan")
    
    # Load existing insights
    insights_md, action_df = load_insights()
    
    # Regenerate button
    if st.button("🔄 Regenerate Suggestions", type="primary"):
        with st.spinner("Generating new insights..."):
            try:
                insights_md, action_df = generate_insights(df)
                st.success("New insights generated successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Error generating insights: {str(e)}")
    
    # Display action plan table
    if not action_df.empty:
        st.subheader("Recommended Actions")
        
        # Color-code priority
        def color_priority(row):
            colors = {
                "高": "background-color: #ff4b4b; color: white;",
                "High": "background-color: #ff4b4b; color: white;",
                "中": "background-color: #ffa724; color: black;",
                "Medium": "background-color: #ffa724; color: black;",
                "低": "background-color: #00cc88; color: white;",
                "Low": "background-color: #00cc88; color: white;"
            }
            return [colors.get(row["priority"], "") for _ in row]
        
        styled_df = action_df.style.apply(color_priority, axis=1)
        st.dataframe(styled_df, use_container_width=True, hide_index=True)
    
    # Display full insights
    if insights_md:
        st.subheader("Detailed Analysis")
        st.markdown(insights_md)
    else:
        st.info("Click 'Regenerate Suggestions' to generate AI-powered insights.")


def render_raw_data_tab(df: pd.DataFrame):
    """Render the Raw Data tab."""
    st.header("Raw KPI Data")
    
    if not df.empty:
        # Show data info
        st.info(f"Showing {len(df)} days of data from {df['date'].min().strftime('%Y-%m-%d')} to {df['date'].max().strftime('%Y-%m-%d')}")
        
        # Display dataframe
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Download button
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"kpi_data_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    else:
        st.warning("No data available to display.")


def render_settings_tab():
    """Render the Settings tab for credential configuration."""
    st.header("⚙️ Settings")
    st.write("Configure your API credentials below. All credentials are encrypted and stored securely.")
    
    # Load existing credentials
    existing_creds = load_credentials() or {}
    
    # Show current status
    st.subheader("Current Configuration Status")
    status = get_credential_status()
    
    col1, col2 = st.columns([1, 2])
    with col1:
        for key, value in status.items():
            st.write(f"**{key}:**")
    with col2:
        for key, value in status.items():
            st.write(value)
    
    st.divider()
    
    # Credential input form
    st.subheader("Update Credentials")
    
    with st.form("credentials_form"):
        # Google Analytics
        st.markdown("### Google Analytics 4")
        ga_help = """To get your GA4 Property ID:
1. Go to [Google Analytics](https://analytics.google.com/)
2. Click ⚙️ Admin → Property Settings
3. Copy the numeric Property ID (e.g., 123456789)"""
        with st.expander("ℹ️ How to get GA4 Property ID"):
            st.markdown(ga_help)
        
        ga_property_id = st.text_input(
            "GA Property ID",
            value=existing_creds.get("GA_PROPERTY_ID", ""),
            placeholder="123456789",
            help="Numeric ID only"
        )
        
        # Stripe
        st.markdown("### Stripe")
        stripe_help = """To get your Stripe API Key:
1. Go to [Stripe Dashboard](https://dashboard.stripe.com/)
2. Click Developers → API keys
3. Copy the Secret key (starts with sk_live_ or sk_test_)"""
        with st.expander("ℹ️ How to get Stripe API Key"):
            st.markdown(stripe_help)
        
        stripe_api_key = st.text_input(
            "Stripe API Key",
            value=existing_creds.get("STRIPE_API_KEY", ""),
            placeholder="sk_live_...",
            type="password",
            help="Starts with sk_live_ or sk_test_"
        )
        
        # OpenAI
        st.markdown("### OpenAI")
        openai_help = """To get your OpenAI API Key:
1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Click API keys
3. Create new secret key
4. Copy the key (starts with sk-)"""
        with st.expander("ℹ️ How to get OpenAI API Key"):
            st.markdown(openai_help)
        
        openai_api_key = st.text_input(
            "OpenAI API Key",
            value=existing_creds.get("OPENAI_API_KEY", ""),
            placeholder="sk-...",
            type="password",
            help="Starts with sk-"
        )
        
        # Twitter (optional)
        st.markdown("### Twitter/X (Optional)")
        twitter_help = """To get your Twitter Bearer Token:
1. Go to [Twitter Developer Portal](https://developer.twitter.com/)
2. Create or select your app
3. Go to Keys and tokens
4. Generate Bearer Token"""
        with st.expander("ℹ️ How to get Twitter Bearer Token"):
            st.markdown(twitter_help)
        
        tw_bearer_token = st.text_input(
            "Twitter Bearer Token (Optional)",
            value=existing_creds.get("TW_BEARER_TOKEN", ""),
            placeholder="AAAAAAAAAAAAAAAA...",
            type="password",
            help="Optional - for auto-posting tweets"
        )
        
        # Submit button
        submitted = st.form_submit_button("💾 Save Credentials", type="primary")
        
        if submitted:
            # Prepare credentials
            new_creds = {
                "GA_PROPERTY_ID": ga_property_id.strip(),
                "STRIPE_API_KEY": stripe_api_key.strip(),
                "OPENAI_API_KEY": openai_api_key.strip(),
                "TW_BEARER_TOKEN": tw_bearer_token.strip()
            }
            
            # Validate
            validations = validate_credentials(new_creds)
            all_valid = all(validations.values())
            
            if all_valid:
                # Save credentials
                if save_credentials(new_creds):
                    st.success("✅ Credentials saved successfully!")
                    st.balloons()
                    st.info("You can now fetch data using the 'Fetch Data' button below.")
                    st.rerun()
                else:
                    st.error("❌ Error saving credentials. Please try again.")
            else:
                # Show validation errors
                st.error("❌ Please fix the following issues:")
                for key, valid in validations.items():
                    if not valid:
                        if key == "GA_PROPERTY_ID":
                            st.error("• GA Property ID must be numeric")
                        elif key == "STRIPE_API_KEY":
                            st.error("• Stripe API Key must start with sk_live_ or sk_test_")
                        elif key == "OPENAI_API_KEY":
                            st.error("• OpenAI API Key must start with sk-")
    
    st.divider()
    
    # Data fetch section
    st.subheader("📊 Fetch Data")
    st.write("Once your credentials are configured, click below to fetch the latest data.")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Fetch Latest Data", type="primary", disabled=not existing_creds):
            with st.spinner("Fetching data from GA4 and Stripe..."):
                try:
                    # Set environment variables
                    for key, value in existing_creds.items():
                        if value:
                            os.environ[key] = value
                    
                    # Fetch data
                    ga_df = fetch_ga_df()
                    stripe_df = fetch_stripe_df()
                    
                    # Create KPI datamart
                    kpi_df = create_kpi_datamart(ga_df, stripe_df)
                    
                    # Save data
                    save_kpi_data(kpi_df)
                    
                    # Generate insights
                    from ai_insight import generate_insights
                    generate_insights(kpi_df)
                    
                    st.success("✅ Data fetched and processed successfully!")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error fetching data: {str(e)}")
                    st.error("Please check your credentials and try again.")
    
    with col2:
        if st.button("🗑️ Clear All Data"):
            if st.checkbox("I understand this will delete all data"):
                try:
                    import shutil
                    if os.path.exists("./output"):
                        shutil.rmtree("./output")
                    st.success("✅ All data cleared successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error clearing data: {str(e)}")
    
    # Show last update time
    if os.path.exists("./output/kpi_daily.csv"):
        mod_time = os.path.getmtime("./output/kpi_daily.csv")
        last_update = datetime.fromtimestamp(mod_time).strftime("%Y-%m-%d %H:%M:%S")
        st.info(f"📅 Last data update: {last_update}")


def main():
    """Main Streamlit application."""
    st.set_page_config(
        page_title="Analytics Dashboard",
        page_icon="📊",
        layout="wide"
    )
    
    # Check if running on Streamlit Cloud
    is_cloud = os.getenv("STREAMLIT_SHARING_MODE") == "true"
    
    # Require password if on cloud or if password is set in secrets
    require_auth = is_cloud or (hasattr(st, "secrets") and "password" in st.secrets)
    
    if require_auth:
        # Add logout button in sidebar
        with st.sidebar:
            st.write(get_login_status())
            if st.button("Logout"):
                logout()
        
        # Check password
        if not check_password():
            st.stop()
    
    st.title("📊 Analytics Dashboard")
    st.caption("Real-time KPI monitoring with AI-powered insights")
    
    # Load data
    df = load_kpi_data()
    
    # Check if credentials are configured
    creds = load_credentials()
    if not creds:
        st.warning("⚠️ Please configure your API credentials in the Settings tab first.")
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Action Plan", "Raw Data", "⚙️ Settings"])
    
    with tab1:
        render_overview_tab(df)
    
    with tab2:
        render_action_plan_tab(df)
    
    with tab3:
        render_raw_data_tab(df)
    
    with tab4:
        render_settings_tab()
    
    # Footer
    st.divider()
    st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


# Required import for matplotlib
import numpy as np

if __name__ == "__main__":
    main()