# Deployment Guide

## Streamlit Cloud Deployment

### Prerequisites
- GitHub account
- Streamlit Cloud account (free at share.streamlit.io)

### Steps

1. **Fork or Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/YOUR_USERNAME/analytics-dashboard.git
   git push -u origin main
   ```

2. **Deploy on Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io/)
   - Click "New app"
   - Select your repository
   - Set main file path to `app.py`
   - Click "Deploy"

3. **Configure Secrets (After Deployment)**
   - In Streamlit Cloud dashboard, go to your app
   - Click "Settings" → "Secrets"
   - Add the following (example format):
   ```toml
   # Initial encryption key (auto-generated on first run)
   encryption_key = "your-generated-key-here"
   ```

4. **Access Your App**
   - Your app will be available at: `https://YOUR_USERNAME-analytics-dashboard-app-XXXXX.streamlit.app`
   - Go to Settings tab to configure API credentials

## Alternative: Local Network Access

If you're having issues with localhost:8501, try:

1. **Use different host**:
   ```bash
   streamlit run app.py --server.address 0.0.0.0
   ```

2. **Check firewall settings**:
   - macOS: System Preferences → Security & Privacy → Firewall
   - Allow incoming connections for Python

3. **Use ngrok for temporary public access**:
   ```bash
   # Install ngrok
   brew install ngrok
   
   # Run Streamlit
   streamlit run app.py &
   
   # Create tunnel
   ngrok http 8501
   ```

## Security Notes

- Never commit `.env` file or `.streamlit/secrets.toml`
- API keys are encrypted when saved through the web interface
- Use environment-specific keys (test vs production)
- Regularly rotate API keys

## Troubleshooting

### "Access Denied" on localhost
- Check if another process is using port 8501: `lsof -i :8501`
- Try a different port: `streamlit run app.py --server.port 8502`
- Disable firewall temporarily to test

### Deployment Issues
- Ensure all dependencies are in `requirements.txt`
- Check Streamlit Cloud logs for errors
- Verify Python version compatibility (3.11+)