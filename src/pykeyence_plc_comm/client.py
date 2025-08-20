from src.pykeyence_plc_comm.protocol import UdpClient
from src.pykeyence_plc_comm.data import WriteCommand, ReadCommand, ReceivedData


class KeyencePlcClient:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.client = UdpClient(host, port)

    def read(self, address: str, count: int) -> str:
        cmd = ReadCommand(
            address=address,
            count=count,
        )
        encoded_cmd = cmd.encode()
        self.client.send(packet=encoded_cmd)
        data = self.client.receive()
        
        return ReceivedData(data=data).decode()

    def write(self, address: str, data: str) -> bool:
        cmd = WriteCommand(
            address=address,
            data=data,
        )
        encoded_cmd = cmd.encode()
        self.client.send(packet=encoded_cmd)
        data = self.client.receive()
        data = ReceivedData(data=data).decode()
        if data.startswith("OK"):
            return True
        else:
            return False
