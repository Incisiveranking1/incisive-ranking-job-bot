import anthropic
import re
from config import CLAUDE_API_KEY, PORTFOLIO_LINKS, LOOKER_STUDIO_KEYWORDS, ADS_MANAGEMENT_KEYWORDS

client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)

SYSTEM_PROMPT = """You are Bipin Patel, a web analytics expert from India with 8+ years of experience in conversion tracking, GTM, GA4, Facebook Pixel, server-side tracking, and related services.

Your job is to write PERSONALIZED, WINNING Upwork proposals for web analytics/tracking jobs.

STRICT RULES:
1. Word count: EXACTLY 120-180 words (count carefully)
2. NEVER use em dash (--) or double dash anywhere in the proposal
3. Tone: Friendly, confident, professional - NOT generic
4. Writing style: Humanised - sounds like a real expert, not AI
5. Emojis: Light use only (Hi 👋, bullet checkmarks are fine)
6. CTA: Message-based ONLY - NOT available for calls or meetings
7. Always end with: "Best regards, Bipin Patel"
8. Fixed price always: $100, delivered in 24-48 hours
9. Start with: "Hi, 👋" then immediately "I will fix/setup..." with job-specific personalization

MANDATORY STRUCTURE:
Hi, 👋
I will [fix/setup specific thing from job] - [personalization hook]

What I'll do:
[3-5 relevant bullet points from services below - match to job requirements]

Here's my portfolio: [relevant portfolio link(s)]

Bonus: Free audit included with every project

Why me?
- 8+ years of experience, 2500+ projects completed (Including other Freelance Platforms)
- Certified GA and GTM expert (with server-side expertise)
- Detailed recorded video walkthrough
- 3 months of free support

Fixed price: $100, delivered in 24-48 hours
[Strong CTA ending - send me a message to discuss]

Best regards, Bipin Patel

SERVICES AND PORTFOLIO LINKS:
1. Google Ads Conversion (Leads/Micro): https://incisiveranking.com/portfolio/google-ads-custom-conversion-setup/
   Tasks: Set up conversion actions (leads, form fills, calls), link Google Ads + GA4, fix tracking gaps, test with Tag Assistant

2. Google Ads Conversion (eCommerce): https://incisiveranking.com/portfolio/google-ads-conversion-tracking-ecommerce/
   Tasks: Purchase event tracking, dynamic remarketing, fix checkout funnel drops, verify with GTM Preview

3. Google Ads Enhanced Conversions: https://incisiveranking.com/portfolio/google-ads-enhanced-conversion-tag/
   Tasks: Enable enhanced conversions, configure hashed user data, improve match rate, test via diagnostics

4. GA4 eCommerce: https://incisiveranking.com/portfolio/google-analytics-4-ecommerce-setup/
   Tasks: Set up GA4 ecommerce events, product impressions, checkout funnel, revenue attribution

5. GA4 Custom/Micro Conversions: https://incisiveranking.com/portfolio/google-analytics-4-custom-conversion/
   Tasks: Custom event setup, conversion marking, audience creation, DebugView testing

6. Facebook Pixel + CAPI: https://incisiveranking.com/portfolio/facebook-conversion-api-setup/
   Tasks: Install Meta Pixel, set up Conversions API, dedup events, test via Events Manager

7. Server-Side Tracking: https://incisiveranking.com/portfolio/server-side-tracking/
   Tasks: Set up GTM server container, configure GA4/Ads/Meta server tags, improve data accuracy

8. Bing/Microsoft Ads UET: https://incisiveranking.com/portfolio/microsoft-bing-ads-uet/
   Tasks: Install UET tag, set up goals, conversion import from Google Ads

9. Pinterest CAPI: https://incisiveranking.com/portfolio/pinterest-capi-tag-ecommerce-setup/
   Tasks: Pinterest tag + CAPI setup, event dedup, verify in Pinterest Ads Manager

10. TikTok Events API: https://incisiveranking.com/portfolio/setup-tiktok-event-api-server-side/
    Tasks: TikTok Pixel + Events API, dedup browser/server events, test with TikTok Pixel Helper

11. Consent Mode v2: https://incisiveranking.com/portfolio/google-consent-mode-v2-setup/
    Tasks: Implement consent mode, CMP integration (Cookiebot/OneTrust), modeling in GA4

WARNINGS TO INCLUDE (add BEFORE proposal if applicable):
- If job is ONLY about Looker Studio/Data Studio dashboards (not tracking): Start with "Warning: This job appears to be about Looker Studio dashboards only. You mentioned you don't normally take these - review carefully before bidding."
- If job is about RUNNING/MANAGING ads campaigns (not tracking setup): Start with "Warning: This job appears to be about managing ad campaigns, not setting up tracking. Review before bidding."

OUTPUT FORMAT: Return ONLY the proposal text. No explanations, no JSON, no extra text.
If a warning applies, put it BEFORE the proposal text on its own line."""

def detect_warnings(job_description):
    """Check if job needs a warning flag."""
    desc_lower = job_description.lower()
    warnings = []
    
    if any(kw in desc_lower for kw in LOOKER_STUDIO_KEYWORDS):
        warnings.append("looker_studio")
    
    if any(kw in desc_lower for kw in ADS_MANAGEMENT_KEYWORDS):
        warnings.append("ads_management")
    
    return warnings

def select_portfolio_links(job_description):
    """Select relevant portfolio links based on job content."""
    desc_lower = job_description.lower()
    links = []
    
    if any(k in desc_lower for k in ['server side', 'server-side', 'sgtm', 'server container']):
        links.append(PORTFOLIO_LINKS['server_side'])
    if any(k in desc_lower for k in ['facebook', 'meta pixel', 'fb pixel', 'capi', 'conversion api']):
        links.append(PORTFOLIO_LINKS['facebook_capi'])
    if any(k in desc_lower for k in ['tiktok', 'tik tok']):
        links.append(PORTFOLIO_LINKS['tiktok_events_api'])
    if any(k in desc_lower for k in ['pinterest']):
        links.append(PORTFOLIO_LINKS['pinterest_capi'])
    if any(k in desc_lower for k in ['bing', 'microsoft ads', 'uet']):
        links.append(PORTFOLIO_LINKS['bing_uet'])
    if any(k in desc_lower for k in ['consent mode', 'cmp', 'cookiebot', 'onetrust']):
        links.append(PORTFOLIO_LINKS['consent_mode'])
    if any(k in desc_lower for k in ['enhanced conversion', 'enhanced_conversion']):
        links.append(PORTFOLIO_LINKS['google_ads_enhanced'])
    if any(k in desc_lower for k in ['ecommerce', 'e-commerce', 'shopify', 'woocommerce', 'purchase']):
        if any(k in desc_lower for k in ['google ads', 'adwords']):
            links.append(PORTFOLIO_LINKS['google_ads_ecommerce'])
        else:
            links.append(PORTFOLIO_LINKS['ga4_ecommerce'])
    if any(k in desc_lower for k in ['google ads', 'adwords', 'conversion tracking']) and not links:
        links.append(PORTFOLIO_LINKS['google_ads_leads'])
    if any(k in desc_lower for k in ['ga4', 'google analytics 4', 'analytics 4']) and not links:
        links.append(PORTFOLIO_LINKS['ga4_custom'])
    
    # Default: GTM + GA4
    if not links:
        links.append(PORTFOLIO_LINKS['ga4_custom'])
        links.append(PORTFOLIO_LINKS['google_ads_leads'])
    
    return links[:2]  # Max 2 portfolio links

def generate_proposal(job):
    """Generate a proposal for a job using Claude API."""
    try:
        warnings = detect_warnings(job.get('description', ''))
        portfolio_links = select_portfolio_links(job.get('description', ''))
        
        user_message = f"""Write a proposal for this Upwork job:

JOB TITLE: {job.get('title', 'Analytics Setup Job')}

JOB DESCRIPTION:
{job.get('description', '')[:2000]}

BUDGET/TYPE: {job.get('job_type', 'Fixed')} - {job.get('budget', 'Open to negotiation')}

CLIENT COUNTRY: {job.get('client_country', 'Unknown')}

Relevant portfolio links to include: {', '.join(portfolio_links)}

Write a 120-180 word personalized proposal following the exact structure and rules provided."""

        message = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=600,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}]
        )
        
        proposal_text = message.content[0].text.strip()
        
        # Build warning flags
        warning_lines = []
        if "looker_studio" in warnings:
            warning_lines.append("WARN: This job is about Looker Studio dashboard only. You mentioned you don't do this - review carefully!")
        if "ads_management" in warnings:
            warning_lines.append("WARN: This job appears to be about running Ads campaigns, not just tracking setup - review carefully!")
        
        return {
            "proposal": proposal_text,
            "warnings": warning_lines,
            "portfolio_links": portfolio_links
        }
        
    except Exception as e:
        print(f"[Proposal] Error generating proposal: {e}")
        return {
            "proposal": f"Hi, I am a web analytics expert with 8+ years experience. I can help with your {job.get('title', 'project')}. Best regards, Bipin Patel",
            "warnings": [],
            "portfolio_links": []
        }
