import requests
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from config import (
    UPWORK_API_KEY, UPWORK_SECRET, SEARCH_KEYWORDS,
    JOB_MAX_AGE_HOURS, MAX_PROPOSALS_FILTER
)

# IST timezone (UTC+5:30)
IST = timezone(timedelta(hours=5, minutes=30))

def get_jobs_via_rss():
    """
    Fetch Upwork jobs via RSS feed (no API approval needed).
    Falls back to this if Upwork API is not approved yet.
    """
    all_jobs = []
    seen_ids = set()
    
    # Use multiple search terms for better coverage
    primary_keywords = [
        "google tag manager conversion tracking",
        "GA4 setup analytics",
        "facebook pixel CAPI setup",
        "server side tracking GTM",
        "google ads conversion tracking",
        "tiktok events API tracking",
        "consent mode v2 setup",
    ]
    
    for keyword in primary_keywords:
        try:
            encoded_kw = requests.utils.quote(keyword)
            url = f"https://www.upwork.com/ab/feed/jobs/rss?q={encoded_kw}&sort=recency&paging=0%3B10&api_params=1&securityToken=&userUid=&orgUid="
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (compatible; JobAlertBot/1.0)',
                'Accept': 'application/rss+xml, application/xml'
            }
            
            resp = requests.get(url, headers=headers, timeout=15)
            if resp.status_code != 200:
                print(f"[Upwork RSS] Status {resp.status_code} for: {keyword}")
                continue
            
            root = ET.fromstring(resp.content)
            channel = root.find('channel')
            if channel is None:
                continue
            
            items = channel.findall('item')
            print(f"[Upwork RSS] Found {len(items)} jobs for: {keyword}")
            
            for item in items:
                job = parse_rss_item(item)
                if job and job['id'] not in seen_ids:
                    seen_ids.add(job['id'])
                    all_jobs.append(job)
            
            time.sleep(2)  # Be respectful of rate limits
            
        except Exception as e:
            print(f"[Upwork RSS] Error for '{keyword}': {e}")
    
    # Filter by age
    cutoff = datetime.now(IST) - timedelta(hours=JOB_MAX_AGE_HOURS)
    fresh_jobs = [j for j in all_jobs if j.get('posted_ist') and j['posted_ist'] > cutoff]
    
    print(f"[Upwork RSS] Total unique jobs: {len(all_jobs)}, Fresh (<{JOB_MAX_AGE_HOURS}h): {len(fresh_jobs)}")
    return fresh_jobs

def parse_rss_item(item):
    """Parse a single RSS item into a job dict."""
    try:
        title = item.findtext('title', '').strip()
        link = item.findtext('link', '').strip()
        description_html = item.findtext('description', '')
        pub_date_str = item.findtext('pubDate', '')
        
        if not link:
            return None
        
        # Extract job ID from URL
        job_id = link.split('~')[-1].replace('/', '') if '~' in link else link[-20:]
        
        # Parse published date
        posted_ist = parse_pub_date(pub_date_str)
        posted_str = posted_ist.strftime('%d %b %Y, %I:%M %p IST') if posted_ist else 'Unknown'
        
        # Extract details from description HTML
        desc_clean = clean_html(description_html)
        
        # Parse job details from description text
        budget = extract_between(desc_clean, 'Budget:', '\n') or extract_between(desc_clean, 'Hourly Range:', '\n') or 'Not specified'
        country = extract_between(desc_clean, 'Country:', '\n') or 'Unknown'
        
        return {
            'id': job_id,
            'title': title,
            'url': link,
            'description': desc_clean[:3000],
            'posted_ist': posted_ist,
            'posted_str': posted_str,
            'job_type': 'Fixed' if 'Budget:' in desc_clean else 'Hourly',
            'budget': budget.strip(),
            'client_country': country.strip(),
            # RSS doesn't provide all details, set defaults
            'proposals_sent': 'N/A',
            'bid_high': 'N/A',
            'bid_avg': 'N/A', 
            'bid_low': 'N/A',
            'client_jobs_posted': 'N/A',
            'client_hire_rate': 'N/A',
            'client_total_spent': 'N/A',
            'client_total_hires': 'N/A',
            'client_rating': 'N/A',
            'client_reviews': 'N/A',
            'payment_verified': 'N/A',
            'last_viewed': 'N/A',
            'skills': [],
        }
    except Exception as e:
        print(f"[Upwork RSS] Parse error: {e}")
        return None

def parse_pub_date(pub_date_str):
    """Parse RSS pubDate string to IST datetime."""
    if not pub_date_str:
        return None
    try:
        # Format: "Thu, 14 May 2026 12:30:00 +0000"
        dt = datetime.strptime(pub_date_str.strip(), '%a, %d %b %Y %H:%M:%S %z')
        return dt.astimezone(IST)
    except ValueError:
        try:
            dt = datetime.strptime(pub_date_str.strip()[:25], '%a, %d %b %Y %H:%M:%S')
            return dt.replace(tzinfo=timezone.utc).astimezone(IST)
        except ValueError:
            return None

def clean_html(html_text):
    """Remove HTML tags and decode entities."""
    import re
    # Remove HTML tags
    clean = re.sub(r'<[^>]+>', ' ', html_text)
    # Decode common HTML entities
    clean = clean.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&nbsp;', ' ').replace('&#39;', "'").replace('&quot;', '"')
    # Clean up whitespace
    clean = re.sub(r'\s+', ' ', clean).strip()
    return clean

def extract_between(text, start, end):
    """Extract text between two markers."""
    try:
        s_idx = text.find(start)
        if s_idx == -1:
            return ''
        s_idx += len(start)
        e_idx = text.find(end, s_idx)
        if e_idx == -1:
            return text[s_idx:s_idx+100]
        return text[s_idx:e_idx]
    except Exception:
        return ''

def get_jobs():
    """
    Main function to get Upwork jobs.
    Uses RSS feed (works without API approval).
    """
    print("[Upwork] Fetching jobs via RSS feed...")
    return get_jobs_via_rss()
