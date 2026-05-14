#!/usr/bin/env python3
"""
Incisive Ranking Job Alert Bot
================================
Automatically scans Upwork for relevant analytics/tracking jobs
and sends Telegram alerts with AI-generated proposals.

Runs every 30 minutes via Railway cron job.
"""

import time
import sys
from datetime import datetime, timezone, timedelta

from config import MAX_ALERTS_PER_RUN
from upwork_jobs import get_jobs
from proposal_generator import generate_proposal
from telegram_notifier import send_job_alert, send_startup_message, send_no_jobs_summary
from job_tracker import is_job_sent, mark_job_sent, cleanup_old_entries, get_stats

# IST timezone
IST = timezone(timedelta(hours=5, minutes=30))

def log(msg):
    """Print with timestamp."""
    ts = datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S IST')
    print(f"[{ts}] {msg}", flush=True)

def run_job_scan():
    """
    Main job scan cycle:
    1. Fetch jobs from Upwork
    2. Filter out already-sent jobs
    3. Generate proposals via Claude AI
    4. Send Telegram alerts
    5. Track sent jobs
    """
    log("=== Starting job scan ===")
    
    # Cleanup old tracker entries
    cleanup_old_entries(days=7)
    stats = get_stats()
    log(f"Tracker: {stats['total_sent']} jobs tracked")
    
    # Step 1: Fetch jobs
    log("Fetching jobs from Upwork...")
    try:
        all_jobs = get_jobs()
    except Exception as e:
        log(f"ERROR fetching jobs: {e}")
        return 0
    
    log(f"Found {len(all_jobs)} relevant fresh jobs")
    
    if not all_jobs:
        log("No jobs found matching criteria")
        return 0
    
    # Step 2: Filter out already-sent jobs
    new_jobs = [j for j in all_jobs if not is_job_sent(j['id'])]
    log(f"New unsent jobs: {len(new_jobs)}")
    
    if not new_jobs:
        log("All jobs already sent - nothing new")
        return 0
    
    # Step 3 & 4: Generate proposals and send alerts
    alerts_sent = 0
    
    for job in new_jobs:
        if alerts_sent >= MAX_ALERTS_PER_RUN:
            log(f"Reached max alerts per run ({MAX_ALERTS_PER_RUN}). Stopping.")
            break
        
        log(f"Processing: {job['title'][:60]}...")
        
        # Generate proposal
        try:
            proposal_result = generate_proposal(job)
            log(f"Proposal generated ({len(proposal_result['proposal'])} chars)")
        except Exception as e:
            log(f"ERROR generating proposal: {e}")
            proposal_result = {"proposal": "Unable to generate proposal.", "warnings": []}
        
        # Send Telegram alert
        try:
            success = send_job_alert(job, proposal_result)
            if success:
                mark_job_sent(job['id'], job['title'])
                alerts_sent += 1
                log(f"Alert sent! ({alerts_sent}/{MAX_ALERTS_PER_RUN})")
                time.sleep(2)  # Small delay between messages
            else:
                log(f"Failed to send alert for: {job['title'][:50]}")
        except Exception as e:
            log(f"ERROR sending alert: {e}")
    
    log(f"=== Scan complete. Sent {alerts_sent} alerts ===")
    return alerts_sent

def main():
    """Entry point - runs once per Railway cron invocation."""
    log("Incisive Ranking Job Alert Bot starting...")
    
    try:
        alerts_sent = run_job_scan()
        log(f"Run complete. {alerts_sent} alerts sent.")
        sys.exit(0)
    except KeyboardInterrupt:
        log("Interrupted by user")
        sys.exit(0)
    except Exception as e:
        log(f"FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
