# app/websocket_client.py

import asyncio
import websockets
import json
from loguru import logger

WS_SERVER_URI = "ws://localhost:27000/ws/transcribe"  # api4sensevoice 的 WebSocket 端点

async def receive_transcriptions():
    try:
        async with websockets.connect(WS_SERVER_URI) as websocket:
            logger.info(f"连接到 WebSocket 服务器: {WS_SERVER_URI}")
            while True:
                message = await websocket.recv()
                try:
                    data = json.loads(message)
                    if data.get("code") == 0:
                        transcription = data.get("data", "")
                        logger.info(f"收到转录结果: {transcription}")
                        # 在这里添加你希望对转录结果进行的处理逻辑
                    elif data.get("code") == 2:
                        speaker = data.get("data", "")
                        logger.info(f"检测到说话人: {speaker}")
                        # 在这里添加说话人检测的处理逻辑
                    else:
                        logger.warning(f"未知消息代码: {data.get('code')}, 内容: {data}")
                except json.JSONDecodeError:
                    logger.error("无法解析 JSON 消息")
    except Exception as e:
        logger.error(f"WebSocket 连接出错: {e}", exc_info=True)

def start_websocket_client():
    asyncio.get_event_loop().run_until_complete(receive_transcriptions())

if __name__ == "__main__":
    start_websocket_client()
