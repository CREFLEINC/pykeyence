from src.pykeyence_plc_link.client import KeyencePlcClient
from src.pykeyence_plc_link.mock.mock_keyence_plc_server import MockKeyencePlcServer


IP = "127.0.0.1"
PORT = 8501


mock_server = MockKeyencePlcServer(ip=IP, port=PORT)
mock_server.start()


client = KeyencePlcClient(host=IP, port=PORT)


value = "AC"
client.write("DM100", value)
print(f"Wrote value '{value}' to DM100.")
res = client.read("DM100")
print(f"Read value from DM100: {res}")
