# PyKeyence Library

키엔스 장비를 파이썬으로 제어하기 위한 라이브러리입니다.
현재는 키엔스 PLC 장치와의 통신을 지원하며, UDP를 통해 ASCII 프로토콜로 데이터를 송수신합니다.


## Features

- **Simple Client Interface**: Easy-to-use client for reading and writing PLC data
- **Real-time Monitoring**: Monitor PLC values with automatic change detection
- **Heartbeat Support**: Keep-alive functionality for PLC connections
- **Mock Server**: Built-in mock PLC server for testing and development
- **Thread-safe**: Safe for use in multi-threaded applications


## Installation

* 첫 번째 방법 : pip 

```bash
# Install the package from PyPI
pip install pykeyence
```

* 두 번째 방법 : git

```bash
# Clone the repository
git clone git@github.com:CREFLEINC/pykeyence.git
cd pykeyence

# Install dependencies using uv (recommended)
uv sync
```

## Quick Start

### Basic PLC Communication

```python
from src.pykeyence_plc_link.client import KeyencePlcClient

# Connect to PLC
client = KeyencePlcClient(host="192.168.0.10", port=8501)

# Read data from PLC
value = client.read("DM100")
print(f"DM100 value: {value}")

# Write data to PLC
success = client.write("DM100", "42")
if success:
    print("Write successful")
```

### Real-time Monitoring

```python
from src.pykeyence_plc_link.client import KeyencePlcClient
from src.pykeyence_plc_link.monitor import PlcMonitor

def on_value_changed(new_value):
    print(f"Value changed: {new_value}")

def on_disconnected():
    print("PLC disconnected!")

client = KeyencePlcClient(host="192.168.0.10", port=8501)

monitor = PlcMonitor(
    client=client,
    address="DM100",
    polling_interval_ms=100,
    on_changed_callback=on_value_changed,
    on_disconnected_callback=on_disconnected
)

monitor.start()
```

### Heartbeat Implementation

```python
from src.pykeyence_plc_link.client import KeyencePlcClient
from src.pykeyence_plc_link.heartbeat import Heartbeat

client = KeyencePlcClient(host="192.168.0.10", port=8501)

heartbeat = Heartbeat(
    client=client,
    address="DM200",  # Heartbeat register
    interval_ms=1000
)

heartbeat.start()
```

## Supported Commands

### Read Commands
- **Single Read**: `RD DM100` - Read one register
- **Multiple Read**: `RDS DM100 10` - Read multiple consecutive registers

### Write Commands
- **Single Write**: `WR DM100 42` - Write single value
- **Multiple Write**: `WRS DM100 5 01 02 03 04 05` - Write multiple values


## Project Structure

```
pykeyence/
├── src/pykeyence_plc_link/
│   ├── client.py          # Main PLC client implementation
│   ├── data.py            # Command builders and data structures
│   ├── protocol.py        # UDP protocol implementation
│   ├── monitor.py         # Real-time monitoring functionality
│   └── heartbeat.py       # Heartbeat implementation
├── examples/
│   ├── plc_client.py      # Basic client usage
│   ├── plc_monitor.py     # Monitoring example
│   └── plc_heartbeat.py   # Heartbeat example
├── mock/
│   └── mock_keyence_plc_server.py  # Mock PLC server for testing
├── tests/
│   └── test_*.py          # Test files
└── pyproject.toml         # Project configuration
```


## API Reference

### KeyencePlcClient

```python
class KeyencePlcClient(PlcClientInterface):
    def __init__(self, host: str, port: int)
    def read(self, address: str, count: int = 1) -> str
    def write(self, address: str, data: str) -> bool
```

### PlcMonitor

```python
class PlcMonitor(threading.Thread):
    def __init__(self, 
                 client: PlcClientInterface, 
                 address: str,
                 count: int = 1,
                 polling_interval_ms: int = 1000,
                 on_changed_callback=None, 
                 on_disconnected_callback=None)
    def start()
    def stop()
```

### Heartbeat

```python
class Heartbeat(threading.Thread):
    def __init__(self, 
                 client: PlcClientInterface, 
                 address: str, 
                 interval_ms: int = 1000, 
                 on_disconnected_callback: callable = None)
    def start()
    def stop()
```


## Development

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src

# Run specific test file
uv run pytest tests/test_pykeyence_plc_link_data.py

# Run with verbose output
uv run pytest -v
```

### Using Mock Server

For development and testing, use the built-in mock PLC server:

```python
from mock.mock_keyence_plc_server import MockKeyencePlcServer

# Start mock server
mock_server = MockKeyencePlcServer(ip="127.0.0.1", port=8501)
mock_server.start()

# Your client code here...

# Stop mock server
mock_server.stop()
```

### Code Style

This project uses standard Python development tools:

```bash
# Format code
black src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/
```

## Configuration

### Default Settings
- **Port**: 8501 (Keyence PLC default UDP port)
- **Timeout**: 1 second for UDP operations
- **Encoding**: ASCII (as required by Keyence protocol)
- **Protocol**: UDP with `\r\n` command termination

### PLC Address Format
- **DM Registers**: `DM100`, `DM200`, etc.
- **Other registers**: Follow Keyence naming convention

## Examples

See the [examples/](examples/) directory for complete working examples:

- [`plc_client.py`](examples/plc_client.py) - Basic read/write operations
- [`plc_monitor.py`](examples/plc_monitor.py) - Real-time value monitoring
- [`plc_heartbeat.py`](examples/plc_heartbeat.py) - Heartbeat implementation

## Protocol Details

This library implements the Keyence ASCII protocol over UDP:

- Commands end with `\r\n` (CRLF)
- Responses are ASCII encoded
- Success responses start with data or "OK"
- Error responses start with "E" followed by error code

### Command Format Examples

```
Single Read:     "RD DM100\r\n"
Multiple Read:   "RDS DM100 10\r\n"
Single Write:    "WR DM100 42\r\n"
Multiple Write:  "WRS DM100 3 01 02 03\r\n"
```

## Requirements

- Python 3.8+
- No external dependencies for core functionality
- pytest, pytest-cov, pytest-mock for development


## Release Notes

### Version 0.1.0
- Initial release
- Basic PLC communication
- Monitoring and heartbeat functionality
- Mock server for testing