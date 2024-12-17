# config/config.py

import os
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()

# 音频流 URL
AUDIO_STREAM_URL = os.getenv('AUDIO_STREAM_URL', 'https://lhttp.qingting.fm/live/339/64k.mp3')

# 转录模式：'single'（单句识别）或 'stream'（流式识别）
TRANSCRIPTION_MODE = os.getenv('TRANSCRIPTION_MODE', 'single')  # 默认使用单句识别

# api4sensevoice HTTP API 端点
HTTP_API_ENDPOINT = os.getenv('HTTP_API_ENDPOINT', 'http://localhost:7000/transcribe')

# api4sensevoice WebSocket 服务器地址
WS_SERVER = os.getenv('WS_SERVER', 'ws://localhost:27000/ws/transcribe')  # 根据实际情况调整
