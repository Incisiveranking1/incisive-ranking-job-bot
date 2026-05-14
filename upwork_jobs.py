import requests
import time
import json
import re
from datetime import datetime, timezone, timedelta
from config import (
    SEARCH_KEYWORDS, JOB_MAX_AGE_HOURS, MAX_PROPOSALS_FILTER
)

# IST timezone (UTC+5:30)
IST = timezone(timedelta(hours=5, minutes=30))

SEARCH_GROUPS = [
    "google+tag+manager+conversion+tracking",
    "GA4+google+analytics+4+setup",
    "facebook+pixel+CAPI+conversion+api",
    "server+side+tracking+GTM",
    "google+ads+conversion+tracking+setup",
    "tiktok+events+api+tracking+setup",
    "consent+mode+v2+cookiebot+setup",
    "ecommerce+tracking+analytics+setup",
    "web+analytics+tracking+consultant",
]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://www.upwork.com/nx/find-work/',
}

def get_jobs():
    """Main function - scrapes Upwork search pages."""
    print("[Upwork] Fetching jobs via web scraping...")
    all_jobs = []
    seen_ids = set()

    for search_query in SEARCH_GROUPS:
        try:
            session = requests.Session()
            session.headers.update(HEADERS)
            url = f'https://www.upwork.com/nx/search/jobs/?q={search_query}&sort=recency&t=0,1'
            resp = session.get(url, timeout=20)
            print(f'[Upwork] Status {resp.status_code} for: {search_query[:40]}')

            if resp.status_code == 200:
                jobs = parse_jobs(resp.text)
                for job in jobs:
                    if job and job['id'] not in seen_ids:
                        seen_ids.add(job['id'])
                        all_jobs.append(job)
                print(f'[Upwork] Extracted {len(jobs)} jobs')
            time.sleep(5)
        except Exception as e:
            print(f'[Upwork] Error: {e}')
            time.sleep(3)

    cutoff = datetime.now(IST) - timedelta(hours=JOB_MAX_AGE_HOURS)
    fresh = [j for j in all_jobs if not j.get('posted_ist') or j['posted_ist'] > cutoff]
    print(f'[Upwork] Total: {len(all_jobs)}, Fresh: {len(fresh)}')
    return fresh


def parse_jobs(html):
    """Extract jobs from Upwork search page HTML/JSON."""
    jobs = []

    # Try to find embedded JSON data (window.__REDUX_STATE__ etc)
    json_patterns = [
        r'"results":\s*(\[.*?\])\s*,\s*"paging"',
        r'"jobPostings":\s*(\[.*?\])',
        r'"data":\s*\{[^}]*"jobs":\s*(\[.*?\])',
    ]
    for pattern in json_patterns:
        try:
            m = re.search(pattern, html, re.DOTALL)
            if m:
                job_list = json.loads(m.group(1))
                for item in job_list[:15]:
                    job = parse_job_dict(item)
                    if job:
                        jobs.append(job)
                if jobs:
                    print(f'[Upwork] Parsed {len(jobs)} from JSON')
                    return jobs
        except Exception:
            pass

    # Fallback: parse HTML article tags
    article_pat = re.compile(r'<article[^>]*>(.*?)</article>', re.DOTALL)
    for m in article_pat.finditer(html):
        job = parse_article(m.group(1))
        if job:
            jobs.append(job)

    return jobs


def parse_job_dict(item):
    """Parse job from dict extracted from JSON state."""
    try:
        title = item.get('title', '') or item.get('jobTitle', '')
        if not title:
            return None
        job_id = str(item.get('id') or item.get('uid') or item.get('ciphertext', title[:20]))
        cipher = item.get('ciphertext', '')
        url = f'https://www.upwork.com/jobs/~{cipher}' if cipher else f'https://www.upwork.com/nx/search/jobs/?q={requests.utils.quote(title)}'
        desc = item.get('snippet', '') or item.get('description', '')
        created = item.get('createdOn', '') or item.get('publishedOn', '')
        posted_ist = parse_iso(created)
        posted_str = posted_ist.strftime('%d %b %Y, %I:%M %p IST') if posted_ist else 'Unknown'
        client = item.get('client', {}) or {}
        country = (client.get('location', {}) or {}).get('country', 'Unknown')
        budget_obj = item.get('budget', {}) or {}
        amount = budget_obj.get('amount', 0) if isinstance(budget_obj, dict) else 0
        budget = f'${amount}' if amount else 'Not specified'
        return {
            'id': job_id, 'title': title, 'url': url,
            'description': desc[:3000], 'posted_ist': posted_ist,
            'posted_str': posted_str,
            'job_type': 'Fixed' if item.get('jobType') == 'FIXED' else 'Hourly',
            'budget': budget, 'client_country': str(country),
            'proposals_sent': str(item.get('proposalsTier', 'N/A')),
            'bid_high': 'N/A', 'bid_avg': 'N/A', 'bid_low': 'N/A',
            'client_jobs_posted': str(client.get('jobsPostedCount', 'N/A')),
            'client_hire_rate': str(client.get('hireRate', 'N/A')),
            'client_total_spent': str(client.get('totalSpent', 'N/A')),
            'client_total_hires': str(client.get('totalHires', 'N/A')),
            'client_rating': str(client.get('totalFeedback', 'N/A')),
            'client_reviews': 'N/A', 'payment_verified': str(client.get('paymentVerificationStatus', 'N/A')),
            'last_viewed': 'N/A', 'skills': item.get('skills', []),
        }
    except Exception as e:
        print(f'[Upwork] parse_job_dict error: {e}')
        return None


def parse_article(html):
    """Parse job from HTML article element."""
    try:
        link_m = re.search(r'href="(/jobs/[^"]+)"', html)
        if not link_m:
            return None
        path = link_m.group(1)
        url = f'https://www.upwork.com{path}'
        job_id = path.split('~')[-1].replace('/', '') if '~' in path else path[-20:]
        title_m = re.search(r'<h[23][^>]*>\s*<[^>]+>([^<]+)<', html)
        title = title_m.group(1).strip() if title_m else path
        desc_m = re.search(r'data-test="job-description[^"]*"[^>]*>([^<]+)', html)
        desc = desc_m.group(1).strip() if desc_m else ''
        time_m = re.search(r'data-test="job-pubtime[^"]*"[^>]*>([^<]+)', html)
        posted_ist = parse_relative(time_m.group(1).strip() if time_m else '')
        posted_str = posted_ist.strftime('%d %b %Y, %I:%M %p IST') if posted_ist else 'Unknown'
        country_m = re.search(r'data-test="client-country[^"]*"[^>]*>([^<]+)', html)
        country = country_m.group(1).strip() if country_m else 'Unknown'
        return {
            'id': job_id, 'title': title, 'url': url,
            'description': desc[:3000], 'posted_ist': posted_ist,
            'posted_str': posted_str, 'job_type': 'Unknown', 'budget': 'N/A',
            'client_country': country, 'proposals_sent': 'N/A',
            'bid_high': 'N/A', 'bid_avg': 'N/A', 'bid_low': 'N/A',
            'client_jobs_posted': 'N/A', 'client_hire_rate': 'N/A',
            'client_total_spent': 'N/A', 'client_total_hires': 'N/A',
            'client_rating': 'N/A', 'client_reviews': 'N/A',
            'payment_verified': 'N/A', 'last_viewed': 'N/A', 'skills': [],
        }
    except Exception as e:
        print(f'[Upwork] parse_article error: {e}')
        return None


def parse_iso(s):
    """Parse ISO datetime to IST."""
    if not s: return None
    try:
        s = s.replace('Z', '+00:00')
        dt = datetime.fromisoformat(s)
        return dt.astimezone(IST)
    except Exception:
        return None


def parse_relative(s):
    """Parse relative time string to IST datetime."""
    if not s: return None
    now = datetime.now(IST)
    s = s.lower()
    try:
        if 'just now' in s or 'second' in s: return now
        n = int(re.search(r'(\d+)', s).group(1))
        if 'minute' in s: return now - timedelta(minutes=n)
        if 'hour' in s: return now - timedelta(hours=n)
        if 'day' in s: return now - timedelta(days=n)
        if 'week' in s: return now - timedelta(weeks=n)
    except Exception:
        pass
    return None