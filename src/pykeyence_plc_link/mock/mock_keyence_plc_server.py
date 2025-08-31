import time
import socket
import threading


class MockKeyencePlcServer(threading.Thread):
    def __init__(self, ip: str, port: int = 3001):
        super().__init__()
        self.ip = ip
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.ip, self.port))
        self.stop_flag = threading.Event()
        self.daemon = True
        self.memory = {}
        print(f"Mock Keyence PLC Server started at {self.ip}:{self.port}")

    def stop(self):
        self.socket.close()
        self.stop_flag.set()
        print("Mock Keyence PLC Server stopped.")

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
        self.stop_flag.clear()
        while not self.stop_flag.is_set():
            time.sleep(0.001)
            data, addr = self.receive()
            if not data:
                continue

            data = data.decode('ascii', errors='ignore')
            if data.startswith('RD') and len(data.split()) == 2:
                key = data.split()[1]
                value = self.memory.get(key, "12336")  # 기본값 설정
                encoded = value.encode('ascii')
                self.send(encoded, addr)
            elif data.startswith('WR') and len(data.split()) == 3:
                key = data.split()[1]
                value = data.split()[2]
                self.memory[key] = value
                response = 'OK'
                encoded = response.encode('ascii')
                self.send(encoded, addr)
           