from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta, timezone
from modules.email_reminder import send_reminder_email
from modules.db import insert_reminder, get_pending_reminders, mark_reminder_sent

scheduler = BackgroundScheduler()

def check_reminders():
    now = datetime.now(timezone.utc)
    for r in get_pending_reminders():
        reminder_id, email, med, time_str = r
        reminder_time = time_str
        trigger_time = reminder_time - timedelta(minutes=15)

        if abs((now - trigger_time).total_seconds()) <= 60:
            print(f"📬 Sending email to {email} at {now.strftime('%I:%M:%S %p')}")
            send_reminder_email(email, med, reminder_time.strftime("%I:%M %p"))
            mark_reminder_sent(reminder_id)

scheduler.add_job(check_reminders, 'interval', minutes=1)
scheduler.start()

def add_reminder(email, med, time_obj):
    print(f"📝 Reminder added: {med} at {time_obj.strftime('%I:%M %p')} for {email}")
    insert_reminder(email, med, time_obj)
