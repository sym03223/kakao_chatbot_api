from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from app.service import enhance_serv
from app import app


def save_guiness_job():
    with app.app_context():
        enhance_serv.save_guiness()

scheduler = BackgroundScheduler(daemon=True)
    
# 매주 일요일 23:59:59에 실행하도록 설정
scheduler.add_job(
    save_guiness_job,
    trigger=CronTrigger(day_of_week='sun', hour=23, minute=59, second=59)
)

