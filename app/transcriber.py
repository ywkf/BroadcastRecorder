# app/transcriber.py

import os
import requests
from app.logging_config import logger

# 配置转录参数
HTTP_API_ENDPOINT = "http://localhost:7000/transcribe"  # api4sensevoice 的 HTTP 转录端点
TRANSCRIPTION_DIR = "transcriptions"

# 确保转录结果目录存在
os.makedirs(TRANSCRIPTION_DIR, exist_ok=True)

def send_http_transcription(audio_file_path, transcription_dir):
    """
    发送音频文件到 HTTP API 进行转录，并保存转录结果。

    Args:
        audio_file_path (str): 需要转录的 WAV 音频文件路径。
        transcription_dir (str): 转录结果保存的目录。
    """
    text_file_path = os.path.join(transcription_dir, f"{os.path.splitext(os.path.basename(audio_file_path))[0]}.txt")
    try:
        logger.info(f"发送音频文件到 HTTP API: {audio_file_path}")
        with open(audio_file_path, 'rb') as audio_file:
            files = {'file': (os.path.basename(audio_file_path), audio_file, 'audio/wav')}
            response = requests.post(HTTP_API_ENDPOINT, files=files)

        logger.debug(f"HTTP 响应状态码: {response.status_code}")
        logger.debug(f"HTTP 响应内容: {response.text}")

        if response.status_code == 200:
            result = response.json()
            if result.get('code') == 0:
                transcription = result.get('data', '')
                if isinstance(transcription, str):
                    save_transcription(transcription, text_file_path)
                    logger.info(f"HTTP 转录成功，结果已保存到: {text_file_path}")
                else:
                    logger.error(f"API 返回的数据格式不正确: {transcription}")
            else:
                logger.error(f"HTTP API 错误: {result.get('msg')}")
        else:
            logger.error(f"HTTP API 返回状态码 {response.status_code}: {response.text}")
    except Exception as e:
        logger.error(f"与 HTTP API 通信出错: {e}", exc_info=True)

def save_transcription(transcription, text_filename):
    """
    保存转录文本到指定文件。

    Args:
        transcription (str): 转录的文本内容。
        text_filename (str): 保存转录文本的文件路径。
    """
    try:
        with open(text_filename, 'w', encoding="utf-8") as f:
            f.write(transcription)
        logger.info(f"转录结果已保存到: {text_filename}")
    except Exception as e:
        logger.error(f"保存转录结果到 {text_filename} 时出错: {e}", exc_info=True)
