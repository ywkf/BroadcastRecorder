# app/recorder.py

import subprocess
import os
from datetime import datetime
from app.logging_config import logger

# 配置录音参数
RATE = 16000              # 16kHz采样率
CHUNK_DURATION = 60       # 每个片段的持续时间（秒）
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RECORDINGS_DIR = os.path.join(BASE_DIR, 'recordings')

# 确保 'recordings' 目录存在
if not os.path.exists(RECORDINGS_DIR):
    os.makedirs(RECORDINGS_DIR)
    logger.info("已创建 'recordings' 目录。")

def record_audio_stream(audio_stream_url, output_filename_prefix, chunk_duration=60):
    """
    从流媒体源录制音频并保存为 WAV 文件。

    Args:
        audio_stream_url (str): 流媒体源的 URL，例如 "https://lhttp.qingting.fm/live/339/64k.mp3".
        output_filename_prefix (str): 录制文件的前缀，通常使用时间戳。
        chunk_duration (int): 每个录制片段的持续时间（秒）。
    """
    logger.info(f"开始录制音频流: {audio_stream_url}")

    for i in range(1, (chunk_duration // 60) + 1):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        wav_filename = os.path.join(RECORDINGS_DIR, f"{output_filename_prefix}_{i}.wav")

        command_wav = [
            'ffmpeg',
            '-y',                         # 覆盖输出文件
            '-i', audio_stream_url,       # 音频流的 URL
            '-acodec', 'pcm_s16le',       # 使用 PCM 编码
            '-ar', str(RATE),             # 采样率 16000 Hz
            '-ac', '1',                   # 单声道
            '-sample_fmt', 's16',         # 16 bit
            '-f', 'wav',                  # 输出格式为 WAV
            '-t', str(chunk_duration),    # 每次录制的持续时间
            wav_filename
        ]

        try:
            logger.debug(f"执行 ffmpeg 命令: {' '.join(command_wav)}")
            result = subprocess.run(command_wav, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            logger.info(f"录制已保存为 WAV: {wav_filename}")
            logger.debug(f"ffmpeg stdout: {result.stdout.decode()}")
            logger.debug(f"ffmpeg stderr: {result.stderr.decode()}")
        except subprocess.CalledProcessError as e:
            logger.error(f"录制 WAV 音频时出错: {e}")
            logger.error(f"ffmpeg stderr: {e.stderr.decode()}")
            continue
        except Exception as e:
            logger.error(f"未知错误: {e}", exc_info=True)
            continue

        # 检查 WAV 文件是否为空
        if os.path.getsize(wav_filename) == 0:
            logger.warning(f"警告: {wav_filename} 文件为空。")
            continue

    return wav_filename
