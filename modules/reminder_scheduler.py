from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta, timezone
from modules.email_reminder import send_reminder_email
from modules.db import insert_reminder, get_pending_reminders, mark_reminder_sent

scheduler = BackgroundScheduler()

def check_reminders():
    now = datetime.now(timezone.utc)  # ✅ aware datetime in UTC

    for r in get_pending_reminders():
        reminder_id, email, med, reminder_time = r

        # ✅ Ensure reminder_time is timezone-aware (assume UTC)
        if reminder_time.tzinfo is None:
            reminder_time = reminder_time.replace(tzinfo=timezone.utc)

        # Calculate trigger time
        trigger_time = reminder_time - timedelta(minutes=15)

        # Debug log
        print(f"⏱️ Now: {now}, Trigger At: {trigger_time}, Diff: {(now - trigger_time).total_seconds()}")

        # Check and send
        if abs((now - trigger_time).total_seconds()) <= 60:
            print(f"📬 Sending email to {email} at {now.strftime('%I:%M:%S %p')}")
            send_reminder_email(email, med, reminder_time.astimezone(timezone.utc).strftime("%I:%M %p"))
            mark_reminder_sent(reminder_id)

scheduler.add_job(check_reminders, 'interval', minutes=1)
scheduler.start()

def add_reminder(email, med, time_obj):
    print(f"📝 Reminder added: {med} at {time_obj.strftime('%I:%M %p')} for {email}")
    insert_reminder(email, med, time_obj)
