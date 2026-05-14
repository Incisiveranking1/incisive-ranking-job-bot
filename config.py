import os

# ============================================================
# INCISIVE RANKING JOB ALERT BOT - CONFIGURATION
# ============================================================
# IMPORTANT: Never commit real API keys to GitHub!
# Set these as Environment Variables in Railway.app

# --- API CREDENTIALS (Set in Railway Environment Variables) ---
UPWORK_API_KEY = os.environ.get("UPWORK_API_KEY", "YOUR_UPWORK_API_KEY")
UPWORK_SECRET = os.environ.get("UPWORK_SECRET", "YOUR_UPWORK_SECRET")
CLAUDE_API_KEY = os.environ.get("CLAUDE_API_KEY", "YOUR_CLAUDE_API_KEY")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "7916487931")

# --- GOOGLE SHEETS (Optional) ---
GOOGLE_SHEET_ID = os.environ.get("GOOGLE_SHEET_ID", "1ACEegtDsSKGLz4Jnm8njbOzH0E1brWJmtdTMjwny_tA")

# --- BOT SETTINGS ---
MAX_ALERTS_PER_RUN = 5        # Max job alerts sent per 30-min cycle
JOB_MAX_AGE_HOURS = 24        # Only show jobs posted in last 24 hours
MAX_PROPOSALS_FILTER = 50     # Skip jobs with more than 50 proposals already
TRACKER_FILE = "sent_jobs.json"  # File to track sent job IDs

# --- UPWORK SEARCH KEYWORDS ---
SEARCH_KEYWORDS = [
    "google tag manager",
    "GTM setup",
    "GA4 setup",
    "google analytics 4",
    "conversion tracking",
    "server side tracking",
    "server-side tagging",
    "facebook pixel",
    "meta pixel",
    "conversion API",
    "CAPI setup",
    "facebook CAPI",
    "google ads conversion",
    "enhanced conversions",
    "ecommerce tracking",
    "GA4 ecommerce",
    "tiktok pixel",
    "tiktok events API",
    "pinterest tag",
    "pinterest CAPI",
    "bing UET",
    "microsoft ads tracking",
    "consent mode v2",
    "CMP setup",
    "cookiebot setup",
    "web analytics",
    "analytics audit",
    "data layer setup",
    "GTM data layer",
    "tag management",
    "tracking setup",
    "remarketing tag",
    "google ads tracking",
    "analytics consultant",
    "web tracking",
]

# --- KEYWORDS THAT INDICATE LOOKER STUDIO JOBS (warn only) ---
LOOKER_STUDIO_KEYWORDS = [
    "looker studio", "data studio", "looker dashboard",
    "google data studio", "reporting dashboard"
]

# --- KEYWORDS THAT INDICATE ADS MANAGEMENT JOBS (warn only) ---
ADS_MANAGEMENT_KEYWORDS = [
    "manage google ads", "run google ads", "google ads management",
    "ppc management", "ads campaign management", "facebook ads management",
    "run facebook ads", "manage facebook ads", "paid ads management",
    "meta ads management", "adwords management"
]

# --- PORTFOLIO LINKS BY SERVICE ---
PORTFOLIO_LINKS = {
    "google_ads_leads": "https://incisiveranking.com/portfolio/google-ads-custom-conversion-setup/",
    "google_ads_ecommerce": "https://incisiveranking.com/portfolio/google-ads-conversion-tracking-ecommerce/",
    "google_ads_enhanced": "https://incisiveranking.com/portfolio/google-ads-enhanced-conversion-tag/",
    "ga4_ecommerce": "https://incisiveranking.com/portfolio/google-analytics-4-ecommerce-setup/",
    "ga4_custom": "https://incisiveranking.com/portfolio/google-analytics-4-custom-conversion/",
    "facebook_capi": "https://incisiveranking.com/portfolio/facebook-conversion-api-setup/",
    "server_side": "https://incisiveranking.com/portfolio/server-side-tracking/",
    "bing_uet": "https://incisiveranking.com/portfolio/microsoft-bing-ads-uet/",
    "pinterest_capi": "https://incisiveranking.com/portfolio/pinterest-capi-tag-ecommerce-setup/",
    "tiktok_events_api": "https://incisiveranking.com/portfolio/setup-tiktok-event-api-server-side/",
    "consent_mode": "https://incisiveranking.com/portfolio/google-consent-mode-v2-setup/",
}
