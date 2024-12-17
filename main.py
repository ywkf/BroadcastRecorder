# main.py

import sys
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import router as api_router  # 导入 API 路由
from app.scheduler import start_scheduler, stop_scheduler  # 导入调度器
from app.config_manager import config_manager  # 导入配置管理器
from loguru import logger
from datetime import datetime
from fastapi.responses import JSONResponse

# 配置 loguru
logger.remove()
log_format = "{time:YYYY-MM-DD HH:mm:ss} [{level}] {message}"
logger.add(sys.stdout, format=log_format, level="DEBUG")
logger.add("logs/main.log", format=log_format, level="INFO")

# 创建 FastAPI 应用
app = FastAPI()

# 设置跨域中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 根据需要指定具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 包含 API 路由
app.include_router(api_router)

# 启动事件
@app.on_event("startup")
def startup_event():
    logger.info("Starting scheduler...")
    start_scheduler()

# 关闭事件
@app.on_event("shutdown")
def shutdown_event():
    logger.info("Stopping scheduler...")
    stop_scheduler()

# 运行应用
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
