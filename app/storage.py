# app/storage.py

import logging
import os
from app.logging_config import logger
# app/storage.py

from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()


class Reminder(Base):
    __tablename__ = 'reminders'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    remind_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


# 创建数据库连接
engine = create_engine('sqlite:///broadcast_recorder.db')
Base.metadata.create_all(engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def save_transcription(transcription, text_filename):
    """
    保存转录文本到指定文件。
    """
    try:
        with open(text_filename, 'w', encoding='utf-8') as f:
            f.write(transcription)
        logger.info(f"转录结果已保存到: {text_filename}")
    except Exception as e:
        logger.error(f"保存转录结果到 {text_filename} 时出错: {e}", exc_info=True)
