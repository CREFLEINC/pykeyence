import socket
import threading


class MockKeyencePlcServer(threading.Thread):
    def __init__(self, ip: str, port: int = 3001):
        super().__init__()
        self.ip = ip
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.ip, self.port))
        self.daemon = True
        self.memory = {
            "DM100": "00000"  # 초기값 설정
        }
        print(f"Mock Keyence PLC Server started at {self.ip}:{self.port}")

    def receive(self, buffer_size: int = 1024):
        try:
            data, addr = self.socket.recvfrom(buffer_size)
            return data, addr
        except Exception as e:
            print(f"Error receiving data: {e}")
            return None, None

    def send(self, packet: bytes, addr: tuple):
        try:
            self.socket.sendto(packet, addr)
        except Exception as e:
            print(f"Error sending data: {e}")

    def run(self):
        print("Mock Keyence PLC Server is running...")
        while True:
            data, addr = self.receive()
            data = data.decode('ascii', errors='ignore') if data else None
            if data == 'RD DM100\r\n':
                response = self.memory["DM100"]
                encoded = response.encode('ascii')
                self.send(encoded, addr)
            elif data.startswith('WR DM100'):
                response = 'OK'
                self.memory["DM100"] = data.split()[2]
                encoded = response.encode('ascii')
                self.send(encoded, addr)