# app/reminders.py

from .storage import SessionLocal, Reminder
from datetime import datetime
from sqlalchemy.orm import Session
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from loguru import logger

scheduler = BackgroundScheduler()
scheduler.start()


def create_reminder(db: Session, title: str, description: str, remind_at: datetime):
    reminder = Reminder(title=title, description=description, remind_at=remind_at)
    db.add(reminder)
    db.commit()
    db.refresh(reminder)

    schedule_reminder(reminder)
    return reminder


def get_reminders(db: Session):
    return db.query(Reminder).all()


def get_reminder(db: Session, reminder_id: int):
    return db.query(Reminder).filter(Reminder.id == reminder_id).first()


def update_reminder(db: Session, reminder_id: int, title: str = None, description: str = None,
                    remind_at: datetime = None):
    reminder = get_reminder(db, reminder_id)
    if not reminder:
        return None
    if title:
        reminder.title = title
    if description:
        reminder.description = description
    if remind_at:
        reminder.remind_at = remind_at
    db.commit()
    db.refresh(reminder)

    schedule_reminder(reminder)
    return reminder


def delete_reminder(db: Session, reminder_id: int):
    reminder = get_reminder(db, reminder_id)
    if not reminder:
        return None
    db.delete(reminder)
    db.commit()
    return reminder


def schedule_reminder(reminder: Reminder):
    trigger = DateTrigger(run_date=reminder.remind_at)
    scheduler.add_job(
        func=send_reminder_notification,
        trigger=trigger,
        args=[reminder.id],
        id=str(reminder.id),
        replace_existing=True
    )
    logger.info(f"Scheduled reminder '{reminder.title}' at {reminder.remind_at}")


def send_reminder_notification(reminder_id: int):
    db = SessionLocal()
    try:
        reminder = get_reminder(db, reminder_id)
        if reminder:
            logger.info(f"提醒: {reminder.title} - {reminder.description} (时间: {reminder.remind_at})")
            # 这里可以集成通知系统，例如发送邮件、推送通知等
    except Exception as e:
        logger.error(f"发送提醒通知时出错: {e}")
    finally:
        db.close()


def load_existing_reminders():
    db = SessionLocal()
    try:
        reminders = db.query(Reminder).filter(Reminder.remind_at >= datetime.utcnow()).all()
        for reminder in reminders:
            schedule_reminder(reminder)
    except Exception as e:
        logger.error(f"加载现有提醒事项时出错: {e}")
    finally:
        db.close()


# 在模块加载时初始化调度
load_existing_reminders()
