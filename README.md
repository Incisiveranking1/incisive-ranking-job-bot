# Incisive Ranking Job Alert Bot

Automated Upwork job scanner for Bipin Patel (@incisiveranking.com).
Scans every 30 minutes for analytics/tracking jobs and sends Telegram alerts with AI-generated proposals.

## How It Works

1. Every 30 minutes, the bot scans Upwork for jobs matching web analytics keywords
2. Filters jobs posted within the last 24 hours
3. Generates a personalized proposal using Claude AI
4. Sends a Telegram alert with job details + ready-made proposal
5. You wake up, check Telegram, click the job link, and paste the proposal

## Files

| File | Purpose |
|------|---------|
| config.py | All settings and keywords |
| upwork_jobs.py | Fetches jobs from Upwork RSS |
| proposal_generator.py | Generates proposals via Claude AI |
| telegram_notifier.py | Sends Telegram alerts |
| job_tracker.py | Prevents duplicate alerts |
| main.py | Main orchestrator |
| requirements.txt | Python dependencies |
| railway.json | Railway.app cron config |

## Setup on Railway.app

### Step 1: Deploy

1. Go to https://railway.app
2. Click "New Project" > "Deploy from GitHub repo"
3. Select this repository: incisive-ranking-job-bot
4. Railway will auto-detect Python and deploy

### Step 2: Set Environment Variables

In Railway dashboard, go to your service > Variables tab and add:

| Variable | Value |
|----------|-------|
| UPWORK_API_KEY | Your Upwork API key |
| UPWORK_SECRET | Your Upwork API secret |
| CLAUDE_API_KEY | Your Claude API key (from console.anthropic.com) |
| TELEGRAM_BOT_TOKEN | Your bot token from @BotFather |
| TELEGRAM_CHAT_ID | 7916487931 |

### Step 3: Verify

The bot will run every 30 minutes automatically.
Check your Telegram (@IR_Job_bot) for the first alert.

## Job Keywords Tracked

- Google Tag Manager / GTM
- GA4 / Google Analytics 4
- Conversion Tracking
- Server-Side Tracking
- Facebook Pixel / Meta CAPI
- Google Ads Conversion
- Enhanced Conversions
- TikTok Events API
- Pinterest CAPI
- Bing UET
- Consent Mode v2
- And 20+ more keywords

## Proposal Format

All proposals follow your exact specifications:
- 120-180 words
- No em dashes
- Fixed price: $100, 24-48hr delivery
- Message-only CTA
- Ends with "Best regards, Bipin Patel"
- Includes relevant portfolio links

## Portfolio Links

- Google Ads (Leads): https://incisiveranking.com/portfolio/google-ads-custom-conversion-setup/
- Google Ads (eCommerce): https://incisiveranking.com/portfolio/google-ads-conversion-tracking-ecommerce/
- GA4 eCommerce: https://incisiveranking.com/portfolio/google-analytics-4-ecommerce-setup/
- Facebook CAPI: https://incisiveranking.com/portfolio/facebook-conversion-api-setup/
- Server-Side: https://incisiveranking.com/portfolio/server-side-tracking/
- Consent Mode v2: https://incisiveranking.com/portfolio/google-consent-mode-v2-setup/
