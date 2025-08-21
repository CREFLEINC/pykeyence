import time
from src.pykeyence_plc_link.mock.mock_keyence_plc_server import MockKeyencePlcServer
from src.pykeyence_plc_link.client import KeyencePlcClient
from src.pykeyence_plc_link.monitor import PlcMonitor


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
mock_server.memory["DM100"] = "00"
time.sleep(1)
mock_server.memory["DM100"] = "AB"
time.sleep(1)
mock_server.stop()
time.sleep(1)
