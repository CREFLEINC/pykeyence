import time
import threading
from .client import PlcClientInterface


class Heartbeat(threading.Thread):
    def __init__(self, client: PlcClientInterface, address: str, interval_ms: int = 1000, on_disconnected_callback: callable = None):
        super().__init__()
        self.daemon = True
        self.client = client
        self.address = address
        self.interval_ms = interval_ms
        self.interval_sec = interval_ms / 1000
        self.stop_flag = threading.Event()
        self.beat = 0
        self.on_disconnected_callback = on_disconnected_callback
        
    def stop(self):
        self.stop_flag.set()        

    def run(self):
        self.stop_flag.clear()
        while not self.stop_flag.is_set():
            try:
                self.beat = 1 if self.beat == 0 else 0
                self.client.write(address=self.address, data=[self.beat])
            except Exception as e:
                if callable(self.on_disconnected_callback):
                    self.on_disconnected_callback()
            time.sleep(self.interval_sec)
