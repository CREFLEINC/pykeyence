import time
import threading
from src.pykeyence_plc_comm.client import PlcClientInterface


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
                    if callable(self.on_changed_callback):
                        self.on_changed_callback(current_value)
                    self.last_value = current_value
                self.is_disconnected = False
            except Exception as e:
                import traceback
                if not self.is_disconnected:
                    self.is_disconnected = True
                    if callable(self.on_disconnected_callback):
                        self.on_disconnected_callback()
                        print(f"PLC와의 연결이 끊어졌습니다: {traceback.format_exc()}")
            time.sleep(self.polling_interval_ms / 1000)


if __name__ == "__main__":
    from src.pykeyence_plc_comm.client import KeyencePlcClient
    from mock.mock_keyence_plc_server import MockKeyencePlcServer

    mock_server = MockKeyencePlcServer(
        ip="127.0.0.1",
        port=8501
    )
    mock_server.start()
    time.sleep(1)

    def on_status_changed(new_value: str):
        print(f"PLC 상태 변경 감지: {new_value}")

    def on_disconnected():
        print("PLC와의 연결이 끊어졌습니다.")

    client = KeyencePlcClient(host="127.0.0.1", port=8501)

    monitor = PlcMonitor(
        client=client,
        address="DM100",
        count=1,
        polling_interval_ms=10,
        on_changed_callback=on_status_changed,
        on_disconnected_callback=on_disconnected
    )
    monitor.start()
    time.sleep(1)
    client.write("DM100", "AB")
    time.sleep(1)
    client.write("DM100", "CD")
    time.sleep(1)
    
