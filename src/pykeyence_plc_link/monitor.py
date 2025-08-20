import time
import threading
from src.pykeyence_plc_link.client import PlcClientInterface


class PlcMonitor(threading.Thread):
    def __init__(self, 
                 client: PlcClientInterface, 
                 address: str,
                 count: int = 1,
                 polling_interval_ms: int = 1000,
                 on_changed_callback=None, 
                 on_disconnected_callback=None):
        super().__init__()
        self.client = client
        self.address = address
        self.count = count
        self.polling_interval_ms = polling_interval_ms
        self.on_changed_callback = on_changed_callback
        self.on_disconnected_callback = on_disconnected_callback
        self.last_value = None
        self.daemon = True
        self.is_disconnected = False
        self.stop_flag = threading.Event()

    def stop(self):
        self.stop_flag.set()

    def run(self):
        self.stop_flag.clear()
        while not self.stop_flag.is_set():
            try:
                current_value = self.client.read(self.address, self.count)
                if current_value != self.last_value:
                    self.last_value = current_value

                    if callable(self.on_changed_callback):
                        self.on_changed_callback(current_value)
                    
                self.is_disconnected = False
            except Exception as e:
                import traceback
                if not self.is_disconnected:
                    self.is_disconnected = True
                    if callable(self.on_disconnected_callback):
                        self.on_disconnected_callback()
                        print(f"PLC와의 연결이 끊어졌습니다: {traceback.format_exc()}")
            time.sleep(self.polling_interval_ms / 1000)

