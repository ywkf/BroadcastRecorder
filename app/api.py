# app/api.py
from fastapi.responses import JSONResponse, FileResponse
from fastapi import APIRouter, File, UploadFile, HTTPException
from pydantic import BaseModel
from typing import List
import os
from datetime import datetime
import logging
from app.config_manager import config_manager
from .storage import get_db, Reminder
from .reminders import create_reminder, get_reminders, get_reminder, update_reminder, delete_reminder

# 创建一个 FastAPI Router
router = APIRouter()

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# 定义请求和响应模型
class ToggleRequest(BaseModel):
    enabled: bool


class FileItem(BaseModel):
    filename: str
    upload_time: str  # ISO格式时间字符串


class TextContent(BaseModel):
    filename: str
    content: str


# 路由：创建提醒事项
@router.post("/api/reminders")
def add_reminder(data: dict):
    title = data.get('title')
    description = data.get('description', '')
    remind_at_str = data.get('remind_at')

    try:
        remind_at = datetime.fromisoformat(remind_at_str)
    except ValueError:
        raise HTTPException(status_code=400, detail='Invalid date format. Use ISO format.')

    db = next(get_db())
    reminder = create_reminder(db, title, description, remind_at)
    return {
        'id': reminder.id,
        'title': reminder.title,
        'description': reminder.description,
        'remind_at': reminder.remind_at.isoformat()
    }


# 路由：获取所有提醒事项
@router.get("/api/reminders")
def list_reminders():
    db = next(get_db())
    reminders = get_reminders(db)
    return [
        {
            'id': r.id,
            'title': r.title,
            'description': r.description,
            'remind_at': r.remind_at.isoformat()
        } for r in reminders
    ]


# 路由：获取单个提醒事项
@router.get("/api/reminders/{reminder_id}")
def get_single_reminder(reminder_id: int):
    db = next(get_db())
    reminder = get_reminder(db, reminder_id)
    if not reminder:
        raise HTTPException(status_code=404, detail='Reminder not found')
    return {
        'id': reminder.id,
        'title': reminder.title,
        'description': reminder.description,
        'remind_at': reminder.remind_at.isoformat()
    }



@router.get("/api/reminders/today")
def list_today_reminders():
    db = next(get_db())
    reminders = get_reminders(db)
    today = datetime.today().date()
    today_reminders = [r for r in reminders if r.remind_at.date() == today]
    return [
        {
            'id': r.id,
            'title': r.title,
            'description': r.description,
            'remind_at': r.remind_at.isoformat()
        } for r in today_reminders
    ]



# 路由：更新提醒事项
@router.put("/api/reminders/{reminder_id}")
def update_reminder_endpoint(reminder_id: int, data: dict):
    title = data.get('title')
    description = data.get('description')
    remind_at_str = data.get('remind_at')
    remind_at = None
    if remind_at_str:
        try:
            remind_at = datetime.fromisoformat(remind_at_str)
        except ValueError:
            raise HTTPException(status_code=400, detail='Invalid date format. Use ISO format.')

    db = next(get_db())
    reminder = update_reminder(db, reminder_id, title, description, remind_at)
    if not reminder:
        raise HTTPException(status_code=404, detail='Reminder not found')
    return {
        'id': reminder.id,
        'title': reminder.title,
        'description': reminder.description,
        'remind_at': reminder.remind_at.isoformat()
    }


# 路由：删除提醒事项
@router.delete("/api/reminders/{reminder_id}")
def delete_reminder_endpoint(reminder_id: int):
    db = next(get_db())
    reminder = delete_reminder(db, reminder_id)
    if not reminder:
        raise HTTPException(status_code=404, detail='Reminder not found')
    return {'message': 'Reminder deleted successfully'}


# 路由：切换 HTTP 转录服务
@router.post("/toggle/http")
def toggle_http(transcription: ToggleRequest):
    config_manager.set_http_enabled(transcription.enabled)
    status = "开启" if transcription.enabled else "关闭"
    return {"message": f"HTTP 转录已{status}."}


# 路由：切换 WebSocket 转录服务
@router.post("/toggle/ws")
def toggle_ws(transcription: ToggleRequest):
    config_manager.set_ws_enabled(transcription.enabled)
    status = "开启" if transcription.enabled else "关闭"
    return {"message": f"WebSocket 转录已{status}."}


# 路由：获取 recordings 目录中的音频文件列表
@router.get("/recordings", response_model=List[FileItem])
async def list_recordings():
    recordings_dir = "recordings"
    if not os.path.exists(recordings_dir):
        raise HTTPException(status_code=404, detail="Recordings directory not found.")

    files = []
    for filename in os.listdir(recordings_dir):
        if filename.lower().endswith(('.wav', '.mp3', '.webm', '.flac')):
            file_path = os.path.join(recordings_dir, filename)
            upload_time = datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
            files.append(FileItem(filename=filename, upload_time=upload_time))

    return files


# 路由：浏览指定的音频文件
@router.get("/recordings/{filename}")
async def get_recording(filename: str):
    recordings_dir = "recordings"
    file_path = os.path.join(recordings_dir, filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Audio file not found.")

    media_type = "audio/wav" if filename.lower().endswith('.wav') else "audio/mpeg" if filename.lower().endswith(
        '.mp3') else "audio/webm" if filename.lower().endswith('.webm') else "audio/flac"

    return FileResponse(path=file_path, media_type=media_type, filename=filename)


# 路由：获取 transcriptions 目录中的文本文件列表
@router.get("/transcriptions", response_model=List[FileItem])
async def list_transcriptions():
    transcriptions_dir = "transcriptions"
    if not os.path.exists(transcriptions_dir):
        raise HTTPException(status_code=404, detail="Transcriptions directory not found.")

    files = []
    for filename in os.listdir(transcriptions_dir):
        if filename.lower().endswith('.txt'):
            file_path = os.path.join(transcriptions_dir, filename)
            upload_time = datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
            files.append(FileItem(filename=filename, upload_time=upload_time))

    return files


# 路由：浏览指定的文本文件内容
@router.get("/transcriptions/{filename}", response_model=TextContent)
async def get_transcription(filename: str):
    transcriptions_dir = "transcriptions"
    file_path = os.path.join(transcriptions_dir, filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Transcription file not found.")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        logger.error(f"Error reading transcription file {filename}: {e}")
        raise HTTPException(status_code=500, detail="Error reading transcription file.")

    return TextContent(filename=filename, content=content)

