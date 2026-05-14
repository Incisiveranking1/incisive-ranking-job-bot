import requests
import time
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

def send_message(text, parse_mode="HTML"):
    """Send a message to the Telegram chat."""
    try:
        resp = requests.post(
            f"{TELEGRAM_API}/sendMessage",
            json={
                "chat_id": TELEGRAM_CHAT_ID,
                "text": text,
                "parse_mode": parse_mode,
                "disable_web_page_preview": True
            },
            timeout=15
        )
        data = resp.json()
        if not data.get("ok"):
            print(f"[Telegram] Error: {data.get('description')}")
            return False
        return True
    except Exception as e:
        print(f"[Telegram] Exception: {e}")
        return False

def format_job_alert(job, proposal_result):
    """Format a complete job alert message for Telegram."""
    
    job_title = job.get('title', 'Unknown Job')
    job_url = job.get('url', '#')
    posted_time = job.get('posted_str', 'Unknown time')
    job_type = job.get('job_type', 'Unknown')
    budget = job.get('budget', 'Not specified')
    description = job.get('description', '')[:600]
    
    # Client info
    client_country = job.get('client_country', 'Unknown')
    client_jobs_posted = job.get('client_jobs_posted', 'N/A')
    client_hire_rate = job.get('client_hire_rate', 'N/A')
    client_total_spent = job.get('client_total_spent', 'N/A')
    client_rating = job.get('client_rating', 'N/A')
    
    # Bid info
    proposals_sent = job.get('proposals_sent', 'N/A')
    bid_high = job.get('bid_high', 'N/A')
    bid_avg = job.get('bid_avg', 'N/A')
    bid_low = job.get('bid_low', 'N/A')
    last_viewed = job.get('last_viewed', 'N/A')
    payment_verified = job.get('payment_verified', 'N/A')
    
    # Proposal and warnings
    warnings = proposal_result.get('warnings', [])
    proposal_text = proposal_result.get('proposal', '')
    
    # Build warning section
    warning_section = ""
    for warn in warnings:
        warning_section += f"\n{warn}\n"
    
    # Truncate description
    desc_preview = description[:500] + "..." if len(description) > 500 else description
    
    message = f"""NEW JOB ALERT! 🚨
{warning_section}
<b>Title:</b> {escape_html(job_title)}
<b>Posted:</b> {posted_time} (IST)
<b>Type:</b> {job_type} | <b>Budget:</b> {escape_html(str(budget))}

<b>Job Link:</b> <a href="{job_url}">Click to View Job</a>

<b>Description Preview:</b>
{escape_html(desc_preview)}

CLIENT INFO:
<b>Country:</b> {client_country}
<b>Jobs Posted:</b> {client_jobs_posted}
<b>Hire Rate:</b> {client_hire_rate}
<b>Total Spent:</b> {client_total_spent}
<b>Rating:</b> {client_rating}
<b>Payment Verified:</b> {payment_verified}

BID INFO:
<b>Proposals Sent:</b> {proposals_sent}
<b>Bid Range:</b> High: {bid_high} | Avg: {bid_avg} | Low: {bid_low}
<b>Last Viewed by Client:</b> {last_viewed}

READY-MADE PROPOSAL:
<pre>{escape_html(proposal_text)}</pre>

Simply copy the proposal above and bid now! 🚀"""
    
    return message

def escape_html(text):
    """Escape HTML special characters for Telegram."""
    if not isinstance(text, str):
        text = str(text)
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def send_job_alert(job, proposal_result):
    """Send a formatted job alert to Telegram."""
    try:
        message = format_job_alert(job, proposal_result)
        
        # Telegram has a 4096 char limit per message
        if len(message) > 4000:
            # Send in two parts
            header_end = message.find("READY-MADE PROPOSAL:")
            if header_end > 0:
                part1 = message[:header_end].strip()
                part2 = "READY-MADE PROPOSAL:\n" + message[header_end + len("READY-MADE PROPOSAL:"):]
                
                send_message(part1)
                time.sleep(1)
                send_message(part2)
            else:
                send_message(message[:4000])
        else:
            send_message(message)
        
        print(f"[Telegram] Alert sent for: {job.get('title', 'Unknown')[:50]}")
        return True
        
    except Exception as e:
        print(f"[Telegram] Error sending alert: {e}")
        return False

def send_startup_message():
    """Send a startup notification."""
    msg = "Bot started! Scanning Upwork for jobs matching your skills... Will alert you every 30 minutes with relevant jobs + proposals. 🤖"
    return send_message(msg)

def send_no_jobs_summary(run_count):
    """Send a summary when no new jobs are found (every 6 runs = 3 hours)."""
    if run_count % 6 == 0:
        msg = f"Scan #{run_count}: No new relevant jobs found in the last 30 minutes. Still watching... 👀"
        send_message(msg)
