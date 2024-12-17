# app/config_manager.py

import threading

class ConfigManager:
    def __init__(self):
        self._lock = threading.Lock()
        self._http_enabled = True  # 默认开启 HTTP 转录
        self._ws_enabled = True    # 默认开启 WebSocket 转录

    def is_http_enabled(self):
        with self._lock:
            return self._http_enabled

    def is_ws_enabled(self):
        with self._lock:
            return self._ws_enabled

    def set_http_enabled(self, enabled: bool):
        with self._lock:
            self._http_enabled = enabled

    def set_ws_enabled(self, enabled: bool):
        with self._lock:
            self._ws_enabled = enabled

# 创建单例实例
config_manager = ConfigManager()
