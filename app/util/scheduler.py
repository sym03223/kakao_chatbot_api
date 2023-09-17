from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from app.service import enhance_serv
from app import app, db
from sqlalchemy import text
from flask import Flask

def save_guiness_job():
    print("시작시작시작")
    with app.app_context():
        try:
            db.session.execute(text("call save_guiness()"))
        except Exception as e:
            print(f"An error occurred: {e}")
    

scheduler = BackgroundScheduler(daemon=True)
    
# 매주 월요일 00:00에 실행하도록 설정
scheduler.add_job(
    save_guiness_job,
    # trigger=CronTrigger(day_of_week='sun', hour=23, minute=59),
    trigger=IntervalTrigger(seconds=3),
)

