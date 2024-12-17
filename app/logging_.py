import logging
import os

# 确保日志目录存在
log_dir = './logs'
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# 配置日志
log_filename = os.path.join(log_dir, 'app_log.txt')
logging.basicConfig(
    level=logging.DEBUG,  # 设置日志级别为 DEBUG（记录所有日志）
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # 设置日志格式
    handlers=[
        logging.FileHandler(log_filename),  # 保存日志到文件
        logging.StreamHandler()  # 同时在控制台输出日志
    ]
)

# 创建日志记录器
logger = logging.getLogger(__name__)

# 示例日志记录
logger.debug("This is a debug message.")
logger.info("This is an info message.")
logger.warning("This is a warning message.")
logger.error("This is an error message.")
logger.critical("This is a critical message.")
