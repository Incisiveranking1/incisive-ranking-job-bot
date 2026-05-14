import json
import os
from datetime import datetime, timedelta
from config import TRACKER_FILE

def load_tracker():
    """Load the tracker file containing sent job IDs."""
    if not os.path.exists(TRACKER_FILE):
        return {}
    try:
        with open(TRACKER_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}

def save_tracker(tracker_data):
    """Save the tracker file."""
    try:
        with open(TRACKER_FILE, 'w') as f:
            json.dump(tracker_data, f, indent=2)
    except IOError as e:
        print(f"[Tracker] Error saving tracker: {e}")

def is_job_sent(job_id):
    """Check if a job has already been sent."""
    tracker = load_tracker()
    return job_id in tracker

def mark_job_sent(job_id, job_title=""):
    """Mark a job as sent to avoid duplicates."""
    tracker = load_tracker()
    tracker[job_id] = {
        "sent_at": datetime.utcnow().isoformat(),
        "title": job_title[:100]  # Store title for reference
    }
    save_tracker(tracker)
    print(f"[Tracker] Marked as sent: {job_id[:20]}...")

def cleanup_old_entries(days=7):
    """Remove entries older than N days to keep file small."""
    tracker = load_tracker()
    cutoff = datetime.utcnow() - timedelta(days=days)
    original_count = len(tracker)
    
    cleaned = {}
    for job_id, data in tracker.items():
        try:
            sent_at = datetime.fromisoformat(data.get("sent_at", ""))
            if sent_at > cutoff:
                cleaned[job_id] = data
        except (ValueError, TypeError):
            pass  # Remove malformed entries
    
    if len(cleaned) < original_count:
        save_tracker(cleaned)
        removed = original_count - len(cleaned)
        print(f"[Tracker] Cleaned up {removed} old entries (>{days} days old)")
    
    return len(cleaned)

def get_stats():
    """Get tracker statistics."""
    tracker = load_tracker()
    return {
        "total_sent": len(tracker),
        "tracker_file": TRACKER_FILE
    }
