import requests
import time
import json
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from config import JOB_MAX_AGE_HOURS

IST = timezone(timedelta(hours=5, minutes=30))

# Keywords for filtering relevant analytics/tracking jobs
RELEVANT_KEYWORDS = [
    'google tag manager', 'gtm', 'ga4', 'google analytics',
    'conversion tracking', 'facebook pixel', 'meta pixel',
    'server side tracking', 'server-side', 'capi', 'conversion api',
    'google ads tracking', 'enhanced conversion', 'tiktok pixel',
    'tiktok events', 'pinterest tag', 'bing uet', 'microsoft ads tracking',
    'consent mode', 'cookiebot', 'web analytics', 'analytics audit',
    'data layer', 'tag management', 'ecommerce tracking', 'analytics setup',
    'tracking setup', 'remarketing tag', 'analytics consultant',
]


def is_relevant(title, description):
    text = (title + ' ' + description).lower()
    return any(kw in text for kw in RELEVANT_KEYWORDS)


# ============================================================
# SOURCE 1: Freelancer.com API (no auth required for public feed)
# ============================================================
def get_freelancer_jobs():
    jobs = []
    # Freelancer public job search API
    skill_ids = [
        '1217',  # Google Analytics
        '1218',  # Google Tag Manager
        '1203',  # Digital Marketing
        '1165',  # SEO
        '1322',  # Facebook Marketing
    ]
    for skill_id in skill_ids[:3]:
        try:
            url = ('https://www.freelancer.com/api/projects/0.1/projects/active/'
                   f'?job_ids[]={skill_id}&limit=20&compact=true'
                   '&project_details=true&job_details=true&full_description=true'
                   '&user_details=true')
            headers = {
                'User-Agent': 'Mozilla/5.0',
                'Accept': 'application/json',
                'Freelancer-OAuth-V1': ''
            }
            r = requests.get(url, headers=headers, timeout=15)
            if r.status_code != 200:
                print(f'[Freelancer] Status {r.status_code} for skill {skill_id}')
                continue
            data = r.json()
            projects = data.get('result', {}).get('projects', {}) or {}
            for pid, proj in projects.items():
                job = parse_freelancer_job(proj)
                if job and is_relevant(job['title'], job['description']):
                    jobs.append(job)
            print(f'[Freelancer] Got {len(projects)} jobs for skill {skill_id}')
            time.sleep(2)
        except Exception as e:
            print(f'[Freelancer] Error: {e}')
    return jobs


def parse_freelancer_job(p):
    try:
        title = p.get('title', '')
        pid = str(p.get('id', ''))
        seo_url = p.get('seo_url', '')
        url = f'https://www.freelancer.com/projects/{seo_url}' if seo_url else f'https://www.freelancer.com/projects/{pid}'
        desc = p.get('description', '') or ''
        budget = p.get('budget', {}) or {}
        b_min = budget.get('minimum', 0)
        b_max = budget.get('maximum', 0)
        budget_str = f'${b_min}-${b_max}' if b_min else 'Not specified'
        ts = p.get('time_submitted', 0)
        if ts:
            posted_ist = datetime.fromtimestamp(ts, tz=timezone.utc).astimezone(IST)
            posted_str = posted_ist.strftime('%d %b %Y, %I:%M %p IST')
        else:
            posted_ist = None
            posted_str = 'Unknown'
        owner = p.get('owner_id', 'Unknown')
        bid_count = p.get('bid_stats', {}).get('bid_count', 'N/A')
        return {
            'id': 'fl_' + pid,
            'title': title,
            'url': url,
            'description': desc[:3000],
            'posted_ist': posted_ist,
            'posted_str': posted_str,
            'job_type': 'Fixed',
            'budget': budget_str,
            'client_country': 'Unknown',
            'proposals_sent': str(bid_count),
            'bid_high': 'N/A', 'bid_avg': 'N/A', 'bid_low': 'N/A',
            'client_jobs_posted': 'N/A',
            'client_hire_rate': 'N/A',
            'client_total_spent': 'N/A',
            'client_total_hires': 'N/A',
            'client_rating': 'N/A',
            'client_reviews': 'N/A',
            'payment_verified': 'N/A',
            'last_viewed': 'N/A',
            'skills': [],
            'source': 'Freelancer.com',
        }
    except Exception as e:
        print(f'[Freelancer] parse error: {e}')
        return None


# ============================================================
# SOURCE 2: People Per Hour (PPH) RSS - works without auth
# ============================================================
def get_pph_jobs():
    jobs = []
    keywords = [
        'google tag manager',
        'GA4 analytics setup',
        'facebook pixel conversion',
        'google ads tracking',
        'server side tracking',
    ]
    for kw in keywords:
        try:
            encoded = requests.utils.quote(kw)
            url = f'https://www.peopleperhour.com/freelance-jobs?q={encoded}&sort=date'
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml',
                'Accept-Language': 'en-US,en;q=0.9',
            }
            r = requests.get(url, headers=headers, timeout=20)
            if r.status_code == 200:
                extracted = parse_pph_html(r.text)
                jobs.extend(extracted)
                print(f'[PPH] Got {len(extracted)} jobs for: {kw}')
            else:
                print(f'[PPH] Status {r.status_code} for: {kw}')
            time.sleep(3)
        except Exception as e:
            print(f'[PPH] Error: {e}')
    return jobs


def parse_pph_html(html):
    jobs = []
    # Find job cards in PPH HTML
    card_pattern = re.compile(
        r'href="(/job-[^"]+)"[^>]*>\s*<[^>]*>([^<]{10,200})</[^>]*>',
        re.DOTALL
    )
    seen = set()
    for m in card_pattern.finditer(html):
        path = m.group(1)
        title = m.group(2).strip()
        if path in seen or not title:
            continue
        seen.add(path)
        job_id = 'pph_' + path.replace('/', '_')
        jobs.append({
            'id': job_id,
            'title': title,
            'url': 'https://www.peopleperhour.com' + path,
            'description': title,
            'posted_ist': datetime.now(IST),
            'posted_str': datetime.now(IST).strftime('%d %b %Y IST'),
            'job_type': 'Fixed',
            'budget': 'See listing',
            'client_country': 'Unknown',
            'proposals_sent': 'N/A',
            'bid_high': 'N/A', 'bid_avg': 'N/A', 'bid_low': 'N/A',
            'client_jobs_posted': 'N/A',
            'client_hire_rate': 'N/A', 'client_total_spent': 'N/A',
            'client_total_hires': 'N/A', 'client_rating': 'N/A',
            'client_reviews': 'N/A', 'payment_verified': 'N/A',
            'last_viewed': 'N/A', 'skills': [],
            'source': 'PeoplePerHour',
        })
    return jobs[:10]


# ============================================================
# SOURCE 3: Upwork via GraphQL API (their internal endpoint)
# ============================================================
def get_upwork_jobs_graphql():
    jobs = []
    search_terms = [
        'google tag manager conversion tracking',
        'GA4 google analytics setup',
        'facebook pixel CAPI setup',
        'server side tracking GTM',
        'google ads conversion tracking',
    ]
    for term in search_terms:
        try:
            # Upwork's internal GraphQL endpoint
            url = 'https://www.upwork.com/api/graphql/v1'
            query = {
                'query': '''query JobSearch($query: String!) {
                  jobSearch(searchQuery: $query, pagination: {first: 10}) {
                    edges {
                      node {
                        id title description
                        publishedDateTime
                        budget { amount currencyCode }
                        client { location { country } }
                      }
                    }
                  }
                }''',
                'variables': {'query': term}
            }
            headers = {
                'User-Agent': 'Mozilla/5.0',
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'X-Upwork-Accept-Language': 'en-US',
            }
            r = requests.post(url, json=query, headers=headers, timeout=15)
            print(f'[Upwork GQL] Status {r.status_code} for: {term[:30]}')
            if r.status_code == 200:
                data = r.json()
                edges = data.get('data', {}).get('jobSearch', {}).get('edges', [])
                for edge in edges:
                    job = parse_graphql_job(edge.get('node', {}))
                    if job:
                        jobs.append(job)
            time.sleep(3)
        except Exception as e:
            print(f'[Upwork GQL] Error: {e}')
    return jobs


def parse_graphql_job(node):
    try:
        if not node.get('title'):
            return None
        job_id = str(node.get('id', ''))
        title = node.get('title', '')
        desc = node.get('description', '')
        created = node.get('publishedDateTime', '')
        posted_ist = parse_iso(created)
        posted_str = posted_ist.strftime('%d %b %Y, %I:%M %p IST') if posted_ist else 'Unknown'
        budget = node.get('budget', {}) or {}
        amount = budget.get('amount', 0)
        country = (node.get('client', {}) or {}).get('location', {}).get('country', 'Unknown')
        return {
            'id': 'upw_' + job_id,
            'title': title,
            'url': f'https://www.upwork.com/jobs/~{job_id}',
            'description': desc[:3000],
            'posted_ist': posted_ist,
            'posted_str': posted_str,
            'job_type': 'Fixed',
            'budget': f'${amount}' if amount else 'N/A',
            'client_country': str(country),
            'proposals_sent': 'N/A',
            'bid_high': 'N/A', 'bid_avg': 'N/A', 'bid_low': 'N/A',
            'client_jobs_posted': 'N/A', 'client_hire_rate': 'N/A',
            'client_total_spent': 'N/A', 'client_total_hires': 'N/A',
            'client_rating': 'N/A', 'client_reviews': 'N/A',
            'payment_verified': 'N/A', 'last_viewed': 'N/A',
            'skills': [],
            'source': 'Upwork',
        }
    except Exception as e:
        print(f'[Upwork GQL] parse error: {e}')
        return None


def parse_iso(s):
    if not s: return None
    try:
        s = s.replace('Z', '+00:00')
        return datetime.fromisoformat(s).astimezone(IST)
    except Exception:
        return None


def get_jobs():
    """
    Fetch jobs from multiple sources:
    1. Freelancer.com (free API)
    2. PeoplePerHour (HTML scraping)
    3. Upwork GraphQL (internal API attempt)
    """
    all_jobs = []
    seen_ids = set()

    print('[Jobs] Trying Freelancer.com API...')
    try:
        fl_jobs = get_freelancer_jobs()
        print(f'[Jobs] Freelancer: {len(fl_jobs)} relevant jobs')
        all_jobs.extend(fl_jobs)
    except Exception as e:
        print(f'[Jobs] Freelancer error: {e}')

    print('[Jobs] Trying Upwork GraphQL...')
    try:
        upw_jobs = get_upwork_jobs_graphql()
        print(f'[Jobs] Upwork GQL: {len(upw_jobs)} jobs')
        all_jobs.extend(upw_jobs)
    except Exception as e:
        print(f'[Jobs] Upwork GQL error: {e}')

    print('[Jobs] Trying PeoplePerHour...')
    try:
        pph_jobs = get_pph_jobs()
        pph_relevant = [j for j in pph_jobs if is_relevant(j['title'], j['description'])]
        print(f'[Jobs] PPH: {len(pph_relevant)} relevant jobs')
        all_jobs.extend(pph_relevant)
    except Exception as e:
        print(f'[Jobs] PPH error: {e}')

    # Deduplicate
    unique_jobs = []
    for job in all_jobs:
        if job['id'] not in seen_ids:
            seen_ids.add(job['id'])
            unique_jobs.append(job)

    # Filter by age
    cutoff = datetime.now(IST) - timedelta(hours=JOB_MAX_AGE_HOURS)
    fresh = [j for j in unique_jobs if not j.get('posted_ist') or j['posted_ist'] > cutoff]

    print(f'[Jobs] Total unique: {len(unique_jobs)}, Fresh (<{JOB_MAX_AGE_HOURS}h): {len(fresh)}')
    return fresh