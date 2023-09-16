from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from app.service import enhance_serv


def save_guiness_job():
    enhance_serv.save_guiness()
    

scheduler = BackgroundScheduler(daemon=True)
    
# 매주 월요일 00:00에 실행하도록 설정
scheduler.add_job(
    save_guiness_job,
    # trigger=CronTrigger(day_of_week='mon', hour=0, minute=0),
    trigger=IntervalTrigger(seconds=10),
)

