import threading
from abc import ABC, abstractmethod
from .protocol import UdpClient
from .data import WriteCommand, ReadCommand, ReceivedData


class PlcClientInterface(ABC):
    @abstractmethod
    def read(self, address: str, count: int = 1) -> str:
        pass

    @abstractmethod
    def write(self, address: str, data: str) -> bool:
        pass


class KeyencePlcClient(PlcClientInterface):
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.client = UdpClient(host, port)
        self._lock = threading.Lock()

    def read(self, address: str, count: int = 1) -> str:
        with self._lock:
            cmd = ReadCommand(address=address, count=count)
            encoded_cmd = cmd.encode()
            self.client.send(packet=encoded_cmd)
            data = self.client.receive()
            return ReceivedData(data=data).decode()

    def write(self, address: str, data: list[str]) -> bool:
        with self._lock:
            cmd = WriteCommand(address=address, data=data)
            encoded_cmd = cmd.encode()
            self.client.send(packet=encoded_cmd)
            data = self.client.receive()
            data = ReceivedData(data=data).decode()
            return data.startswith("OK")
