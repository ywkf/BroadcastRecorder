# BroadcastRecorder

## 项目简介

BroadcastRecorder 是一个用于录制音频流并进行转录的 Python 项目。它支持两种转录方式：

1. **HTTP 转录**：通过 HTTP API 将音频文件发送至转录服务。
2. **WebSocket 转录**：通过 WebSocket 实时发送音频数据并接收转录结果。

项目还提供了 API 接口，用于实时开启和关闭这两种转录方式。

## 目录结构

BroadcastRecorder/
├── app/
│   ├── __init__.py
│   ├── api.py
│   ├── config_manager.py
│   ├── logging.py
│   ├── logging_config.py
│   ├── recorder.py
│   ├── scheduler.py
│   ├── signal_monitor.py
│   ├── storage.py
│   ├── transcriber.py
│   └── websocket_client.py
├── client/
│   └── client_wss.html
├── config/
│   └── config.py
├── logs/
├── recordings/
├── speaker/
│   ├── speaker1_a_cn_16k.wav
├── transcriptions/
├── tests/
│   └── test_transcription.py
├── main.py
├── requirements.txt
└── README.md


## 安装依赖

确保你使用的是 Python 3.7 及以上版本。

1. **创建并激活虚拟环境**：

    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```

2. **安装依赖**：

    ```bash
    pip install -r requirements.txt
    ```

## 配置环境变量

在项目根目录下创建一个 `.env` 文件，内容如下：

```env
AUDIO_STREAM_URL=https://lhttp.qingting.fm/live/339/64k.mp3
TRANSCRIPTION_MODE=stream  # 或 'single'
HTTP_API_ENDPOINT=http://localhost:8888/transcribe
WS_SERVER=ws://localhost:27000/ws/transcribe
```

## 启动项目
1. **启动 HTTP API 服务器：**
python app/server.py
2. **启动 WebSocket 服务器：**
python app/server_wss.py --port 27000
3. **启动主程序（同时启动 API 服务器和调度器）：**
python app/main.py

## 使用 API 开启或关闭转录方式
**开启或关闭 HTTP 转录：**

**开启 HTTP 转录：**

curl 
-X POST "http://localhost:8000/toggle/http" -H "Content-Type: application/json" -d '{"enabled": true}'

**关闭 HTTP 转录：**

curl 
-X POST "http://localhost:8000/toggle/http" -H "Content-Type: application/json" -d '{"enabled": false}'


**开启或关闭 WebSocket 转录：**

**开启 WebSocket 转录：**

curl -X POST "http://localhost:8000/toggle/ws" -H "Content-Type: application/json" -d '{"enabled": true}'

**关闭 WebSocket 转录：**

curl -X POST "http://localhost:8000/toggle/ws" -H "Content-Type: applicat
## 测试转录功能
1. 使用 WebSocket 客户端
打开 client/client_wss.html 页面：

在浏览器中打开 client/client_wss.html 文件。

选择音频文件：

选择一个符合要求的 .wav 文件（WAV，16kHz，单声道，16位 PCM）。

发送音频文件：

点击“发送音频”按钮，开始发送音频数据。

查看转录结果：

转录结果将显示在页面下方的 <pre> 标签中。

2. 使用测试脚本
确保 HTTP API 服务器已启动，并有一个测试音频文件 recordings/test_audio.wav。

运行测试脚本：

bash
复制代码
python tests/test_transcription.py
查看输出和 transcriptions/test_audio.wav.txt 文件以确认转录结果。
## 添加说话人验证（可选）
准备说话人音频文件：

确保说话人音频文件符合要求（16000 Hz，单声道，16位 PCM，WAV 格式），并放置在 speaker/ 目录下。

修改 app/server_wss.py 中的说话人文件列表：

python
复制代码
reg_spks_files = [
    "speaker/speaker1_a_cn_16k.wav",
    "speaker/speaker2_b_cn_16k.wav"
    # 添加更多说话人文件
]
启用说话人验证：

在客户端 WebSocket URL 中添加 sv=1 参数：

javascript
复制代码
const sv = 1; // 启用说话人验证
const wsUrl = `ws://localhost:27000/ws/transcribe${sv ? '?sv=1' : ''}`;
# BroadcastRecorder
