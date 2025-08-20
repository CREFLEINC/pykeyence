import socket
import abc


class EthernetProtocol(abc.ABC):
    @abc.abstractmethod
    def send(self, packet: bytes):
        pass

    @abc.abstractmethod
    def receive(self, buffer_size: int = 1024):
        pass


class UdpClient(EthernetProtocol):
    def __init__(self, ip: str, port: int = 3001, timeout=0.001):
        super().__init__()
        self.ip = ip
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(timeout)

    def send(self, packet: bytes):
        self.socket.sendto(packet, (self.ip, self.port))

    def receive(self, buffer_size: int = 1024):
        try:
            return self.socket.recvfrom(buffer_size)
        except socket.timeout:
            pass
        except Exception as e:
            print(e)


class TcpClient(EthernetProtocol):
    def __init__(self, ip: str, port: int = 2001, timeout=0.01):
        super().__init__()
        # TODO : To be implemented.

    def send(self, packet: bytes):
        # TODO : To be implemented.
        pass

    def receive(self, buffer_size: int = 1024):
        # TODO : To be implemented.
        pass
