import time
import threading
from src.pykeyence_plc_link.client import PlcClientInterface


class Heartbeat(threading.Thread):
    def __init__(self, client: PlcClientInterface, address: str, interval_ms: int = 1000):
        super().__init__()
        self.daemon = True
        self.client = client
        self.address = address
        self.interval_ms = interval_ms
        self.interval_sec = interval_ms / 1000
        self.stop_flag = threading.Event()
        self.beat = False
        
    def stop(self):
        self.stop_flag.set()        

    def run(self):
        self.stop_flag.clear()
        while not self.stop_flag.is_set():
            try:
                self.beat = not self.beat
                self.client.write(address=self.address, data=str(int(self.beat)))
            except Exception as e:
                print(f"Heartbeat failed: {e}")
            time.sleep(self.interval_sec)

