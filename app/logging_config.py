# app/logging_config.py

import logging
import os
from datetime import datetime

# 定义项目根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 定义日志目录
LOGS_DIR = os.path.join(BASE_DIR, 'logs')

# 创建日志目录（如果不存在）
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)

# 设置日志文件名
log_filename = datetime.now().strftime("app_log_%Y-%m-%d.txt")
log_filepath = os.path.join(LOGS_DIR, log_filename)

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,  # 设置日志级别
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filepath, encoding='utf-8'),
        logging.StreamHandler()  # 同时输出到控制台
    ]
)

logger = logging.getLogger(__name__)
