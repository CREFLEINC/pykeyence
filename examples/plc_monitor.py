from src.pykeyence_plc_link.mock.mock_keyence_plc_server import MockKeyencePlcServer
from src.pykeyence_plc_link.client import KeyencePlcClient
from src.pykeyence_plc_link.monitor import PlcMonitor

PORT = 1234

mock_server = MockKeyencePlcServer(
    ip="127.0.0.1",
    port=PORT
)
mock_server.start()


def on_status_changed(new_value: str):
    print(f"PLC 상태 변경 감지: {new_value}")

def on_disconnected():
    print("PLC와의 연결이 끊어졌습니다.")


client = KeyencePlcClient(host="127.0.0.1", port=PORT)

monitor_a = PlcMonitor(
    client=client,
    address="DM100",
    count=1,
    polling_interval_ms=10,
    on_changed_callback=on_status_changed,
    on_disconnected_callback=on_disconnected
)

monitor_b = PlcMonitor(
    client=client,
    address="DM200",
    count=1,
    polling_interval_ms=10,
    on_changed_callback=on_status_changed,
    on_disconnected_callback=on_disconnected
)


monitor_a.start()
monitor_b.start()

while True:
    x = str(input())
    if x == "0":
        mock_server.memory["DM100"] = "00000"
        mock_server.memory["DM200"] = "00000"
    elif x == "1":
        mock_server.memory["DM100"] = "11111"
    elif x == "2":
        mock_server.memory["DM200"] = "99999"
    elif x == "q":
        break