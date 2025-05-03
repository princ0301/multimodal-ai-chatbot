from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from modules.email_reminder import send_reminder_email

reminders = []

scheduler = BackgroundScheduler()

def check_reminders():
    now = datetime.now()

    for r in reminders[:]:
        reminder_time = r["time"]
        reminder_trigger_time = reminder_time - timedelta(minutes=15)

        time_diff_seconds = (now - reminder_trigger_time).total_seconds()
        print(f"⏱️ Now: {now}, Trigger At: {reminder_trigger_time}, Diff: {time_diff_seconds} seconds")

        if abs(time_diff_seconds) <= 60:
            print(f"📬 Sending email to {r['email']} at {now.strftime('%I:%M:%S %p')}")
            send_reminder_email(r["email"], r["med"], reminder_time.strftime("%I:%M %p"))
            reminders.remove(r)

scheduler.add_job(check_reminders, 'interval', minutes=1)
scheduler.start()
 
def add_reminder(email, med, time_obj):
    print(f"📝 Reminder added: {med} at {time_obj.strftime('%I:%M %p')} for {email}")
    reminders.append({"email": email, "med": med, "time": time_obj})
