# app/websocket_server.py

import asyncio
import websockets
import json

from main import app
from .storage import SessionLocal, Reminder
from datetime import datetime
from loguru import logger

connected_clients = set()

async def handler(websocket, path):
    logger.info("新客户端连接")
    connected_clients.add(websocket)
    try:
        async for message in websocket:
            logger.info(f"收到消息: {message}")
            # 根据需求处理客户端消息
    except websockets.exceptions.ConnectionClosed:
        logger.info("客户端连接关闭")
    finally:
        connected_clients.remove(websocket)

async def send_reminder(reminder):
    if connected_clients:
        message = json.dumps({
            'id': reminder.id,
            'title': reminder.title,
            'description': reminder.description,
            'remind_at': reminder.remind_at.isoformat()
        })
        await asyncio.wait([client.send(message) for client in connected_clients])
        logger.info(f"发送提醒到 {len(connected_clients)} 个客户端")

# 修改 reminders.py 中的 send_reminder_notification 函数
from .reminders import send_reminder_notification, get_reminder


def send_reminder_notification(reminder_id: int):
    db = SessionLocal()
    try:
        reminder = get_reminder(db, reminder_id)
        if reminder:
            logger.info(f"提醒: {reminder.title} - {reminder.description} (时间: {reminder.remind_at})")
            # 通过 WebSocket 发送提醒
            asyncio.run(send_reminder(reminder))
    except Exception as e:
        logger.error(f"发送提醒通知时出错: {e}")
    finally:
        db.close()

def start_websocket_server():
    start_server = websockets.serve(handler, "0.0.0.0", 27000)
    asyncio.get_event_loop().run_until_complete(start_server)
    logger.info("WebSocket 服务器已启动在 ws://0.0.0.0:27000/ws/reminders")
    asyncio.get_event_loop().run_forever()

# 在 main.py 中启动 WebSocket 服务器
if __name__ == "__main__":
    from threading import Thread
    websocket_thread = Thread(target=start_websocket_server, daemon=True)
    websocket_thread.start()
    logger.info("开始 BroadcastRecorder...")
    app.run(host='0.0.0.0', port=5000, debug=True)
