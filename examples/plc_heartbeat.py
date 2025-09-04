import time
from src.pykeyence_plc_link.mock.mock_keyence_plc_server import MockKeyencePlcServer
from src.pykeyence_plc_link.client import KeyencePlcClient
from src.pykeyence_plc_link.heartbeat import Heartbeat


mock_server = MockKeyencePlcServer(
    ip="127.0.0.1",
    port=8501
)
mock_server.start()
time.sleep(1)



client = KeyencePlcClient(host="127.0.0.1", port=8501)

heartbeat = Heartbeat(
    client=client,
    address="DM100",
    interval_ms=1000
)
heartbeat.start()

start_time = time.time()
while time.time() - start_time < 5:
    time.sleep(0.1)
    print(mock_server.memory["DM100"])


