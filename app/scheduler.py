# app/scheduler.py

import os
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from app.recorder import record_audio_stream  # 修改为使用录音器模块
from app.transcriber import send_http_transcription  # 修改为使用转录器模块
from app.config_manager import config_manager  # 假设 config_manager.py 提供 is_http_enabled()
from loguru import logger

RECORDINGS_DIR = "recordings"
TRANSCRIPTIONS_DIR = "transcriptions"
AUDIO_STREAM_URL = "https://lhttp.qingting.fm/live/339/64k.mp3"
MAX_RECORDING_TIME = 2  # 分钟

scheduler = BackgroundScheduler()

def clear_recordings_folder():
    """
    清空录音和转录文件夹。
    """
    if os.path.exists(RECORDINGS_DIR):
        for filename in os.listdir(RECORDINGS_DIR):
            file_path = os.path.join(RECORDINGS_DIR, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                logger.error(f"删除文件 {file_path} 时出错: {e}")
    if os.path.exists(TRANSCRIPTIONS_DIR):
        for filename in os.listdir(TRANSCRIPTIONS_DIR):
            file_path = os.path.join(TRANSCRIPTIONS_DIR, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                logger.error(f"删除文件 {file_path} 时出错: {e}")

def job():
    """
    执行一次录制和转录任务，每次录制最多 2 分钟，分割成 1 分钟片段。
    """
    audio_stream_url = AUDIO_STREAM_URL
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    logger.debug(f"任务开始于 {current_time}")

    # 确保目录存在
    for directory in [RECORDINGS_DIR, TRANSCRIPTIONS_DIR]:
        if not os.path.exists(directory):
            os.makedirs(directory)
            logger.info(f"已创建目录: {directory}")
        else:
            logger.debug(f"目录已存在: {directory}")

    # 录制音频并保存为 WAV 格式
    output_filename_prefix = f"{current_time}"
    wav_file_path = record_audio_stream(audio_stream_url, output_filename_prefix, chunk_duration=60)  # 录制每个片段 60 秒

    logger.info(f"录制完成。文件路径: {wav_file_path}")

    # 处理录制的音频文件并转写
    if os.path.exists(wav_file_path):
        # 检查 HTTP 转录是否启用
        if config_manager.is_http_enabled():
            send_http_transcription(wav_file_path, TRANSCRIPTIONS_DIR)
            logger.info(f"HTTP 模式转录已完成: {wav_file_path}")

        # 检查 WebSocket 转录是否启用（可选，后续实现）
        # if config_manager.is_ws_enabled():
        #     send_ws_transcription(wav_file_path, TRANSCRIPTIONS_DIR)
        #     logger.info(f"WebSocket 模式转录已完成: {wav_file_path}")
    else:
        logger.warning(f"WAV 文件不存在: {wav_file_path}")

def start_scheduler():
    """
    启动任务调度器，定期执行任务。
    """
    # 每周日凌晨 00:00 清空录音文件夹
    scheduler.add_job(clear_recordings_folder, 'cron', day_of_week='sun', hour=0, minute=0)

    # 每 2 分钟执行一次录制和转录任务
    scheduler.add_job(job, 'interval', minutes=MAX_RECORDING_TIME)

    scheduler.start()
    logger.info("调度器已启动。")

def stop_scheduler():
    """
    停止任务调度器。
    """
    scheduler.shutdown()
    logger.info("调度器已停止。")
