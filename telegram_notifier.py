import requests
import time
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

TELEGRAM_API = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}'

def send_message(text, parse_mode='HTML'):
    try:
        resp = requests.post(
            f'{TELEGRAM_API}/sendMessage',
            json={
                'chat_id': TELEGRAM_CHAT_ID,
                'text': text,
                'parse_mode': parse_mode,
                'disable_web_page_preview': True
            },
            timeout=15
        )
        data = resp.json()
        if not data.get('ok'):
            print(f'[Telegram] Error: {data.get("description")}')
            return False
        return True
    except Exception as e:
        print(f'[Telegram] Exception: {e}')
        return False


def escape_html(text):
    if not isinstance(text, str):
        text = str(text)
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def format_job_alert(job, proposal_result):
    source = job.get('source', 'Upwork')
    source_emoji = {'Upwork': '', 'Freelancer.com': '', 'PeoplePerHour': ''}.get(source, '')

    warnings = proposal_result.get('warnings', [])
    warning_section = ''
    for w in warnings:
        warning_section += f'\n{escape_html(w)}\n'

    desc = job.get('description', '')[:500]
    desc_preview = (desc + '...') if len(job.get('description', '')) > 500 else desc

    msg = f'''NEW JOB ALERT! {source_emoji}
{warning_section}
<b>Platform:</b> {source}
<b>Title:</b> {escape_html(job.get('title', ''))}
<b>Posted:</b> {job.get('posted_str', 'Unknown')} (IST)
<b>Type:</b> {job.get('job_type', 'N/A')} | <b>Budget:</b> {escape_html(str(job.get('budget', 'N/A')))}

<b>Job Link:</b> <a href="{job.get('url', '#')}">Click to View Job</a>

<b>Description:</b>
{escape_html(desc_preview)}

CLIENT INFO:
<b>Country:</b> {job.get('client_country', 'N/A')}
<b>Jobs Posted:</b> {job.get('client_jobs_posted', 'N/A')}
<b>Hire Rate:</b> {job.get('client_hire_rate', 'N/A')}
<b>Total Spent:</b> {job.get('client_total_spent', 'N/A')}
<b>Rating:</b> {job.get('client_rating', 'N/A')}
<b>Payment Verified:</b> {job.get('payment_verified', 'N/A')}

BID INFO:
<b>Proposals Sent:</b> {job.get('proposals_sent', 'N/A')}
<b>Bid Range:</b> High: {job.get('bid_high', 'N/A')} | Avg: {job.get('bid_avg', 'N/A')} | Low: {job.get('bid_low', 'N/A')}
<b>Last Viewed:</b> {job.get('last_viewed', 'N/A')}

READY-MADE PROPOSAL:
<pre>{escape_html(proposal_result.get('proposal', ''))}</pre>

Copy the proposal above and bid now! '''
    return msg


def send_job_alert(job, proposal_result):
    try:
        message = format_job_alert(job, proposal_result)
        if len(message) > 4000:
            split = message.find('READY-MADE PROPOSAL:')
            if split > 0:
                send_message(message[:split].strip())
                time.sleep(1)
                send_message('READY-MADE PROPOSAL:\n<pre>' + escape_html(proposal_result.get('proposal', '')) + '</pre>')
            else:
                send_message(message[:4000])
        else:
            send_message(message)
        print(f'[Telegram] Alert sent: {job.get("title", "")[:50]}')
        return True
    except Exception as e:
        print(f'[Telegram] Error: {e}')
        return False


def send_startup_message():
    msg = 'Bot started! Scanning Upwork, Freelancer & PPH for analytics jobs every 30 minutes.'
    return send_message(msg)


def send_no_jobs_summary(run_count):
    if run_count % 6 == 0:
        send_message(f'Scan #{run_count}: No new relevant jobs found. Still watching...')