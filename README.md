# PyKeyence Library

키엔스 장비를 파이썬으로 제어하기 위한 라이브러리입니다.
현재는 키엔스 PLC 장치와의 통신을 지원하며, UDP를 통해 ASCII 프로토콜로 데이터를 송수신합니다.


## Features

- **Simple Client Interface**: Easy-to-use client for reading and writing PLC data
- **Real-time Monitoring**: Monitor PLC values with automatic change detection
- **Heartbeat Support**: Keep-alive functionality for PLC connections
- **Mock Server**: Built-in mock PLC server for testing and development
- **Thread-safe**: Safe for use in multi-threaded applications
- **Enhanced Data Conversion Utilities**: Improved utilities for string-to-decimal conversion with endian support and PLC-specific formatting
- **Flexible Data Handling**: Automatic handling of odd-length data with zero-padding and PLC-compatible 5-digit format
- **Unicode String Parsing**: Built-in support for parsing PLC continuous data into unicode strings


## Installation

* pip 을 사용하는 경우.

```bash
# Install the package from PyPI
pip install pykeyence
```

* git 을 사용하는 경우

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
from pykeyence_plc_link import KeyencePlcClient

# Connect to PLC
client = KeyencePlcClient(host="192.168.0.10", port=8501)

# Read data from PLC 
value = client.read("DM100")  # Returns list[str]
print(f"DM100 value: {value}")

# Write data to PLC (supports both integer and list of integers)
success = client.write("DM100", 42)  # Single integer
if success:
    print("Write successful")

# Write multiple values
success = client.write("DM100", [42, 100, 255])  # List of integers
if success:
    print("Multiple write successful")
```


### Real-time Monitoring

```python
from pykeyence_plc_link import KeyencePlcClient, PlcMonitor

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
from pykeyence_plc_link import KeyencePlcClient, Heartbeat

client = KeyencePlcClient(host="192.168.0.10", port=8501)

heartbeat = Heartbeat(
    client=client,
    address="DM200",  # Heartbeat register
    interval_ms=1000
)

heartbeat.start()
```


## Data Handling and Conversion

### PLC Data Format

The library now supports PLC-specific data formatting where data is automatically converted to 5-digit zero-padded strings (e.g., "00001", "00100"):

```python
from pykeyence_plc_link.client import KeyencePlcClient

client = KeyencePlcClient(host="192.168.0.10", port=8501)

# Data is automatically formatted as 5-digit strings for PLC compatibility
client.write("DM100", 1)      # Becomes "00001" internally
client.write("DM100", 100)    # Becomes "00100" internally
client.write("DM100", 99999)  # Becomes "99999" internally
```

### Enhanced Data Conversion Utilities

Use the improved `CharConverter` class for manual data conversion:

```python
from pykeyence_plc_link import CharConverter

# Convert string to 16-bit decimal (returns 5-digit formatted string)
decimal_value = CharConverter.string_to_16bit_decimal("AB", "little")
print(f"AB (little endian): {decimal_value}")  # Output: "16961"

decimal_value = CharConverter.string_to_16bit_decimal("AB", "big")
print(f"AB (big endian): {decimal_value}")     # Output: "16706"

# Convert 16-bit decimal back to string
string_value = CharConverter.decimal_16bit_to_string(16961)
print(f"16961 -> {string_value}")  # Output: AB
```

### Unicode String Parsing

New utility function for parsing PLC continuous data into unicode strings:

```python
from pykeyence_plc_link import decode_plc_data_to_unicode

# Example with BCR data
bcr_data = ['12662', '13108', '12333', '12336', '13108', '12098', '13362', '13616', '12337', '12335', '12336', '13366']
result = decode_plc_data_to_unicode(bcr_data, byteorder="little")
print(f"BCR string: {result}")  # Output: "V143-00043B/240510/00064"
```

### Endian Support

The library supports both little and big endian byte orders:

```python
from pykeyence_plc_link.data import WriteCommand

# Little endian (default)
cmd_little = WriteCommand(address="DM100", data="AB", byteorder="little")
result_little = cmd_little.encode()
# Result: b"WR DM100 16961\r\n"

# Big endian
cmd_big = WriteCommand(address="DM100", data="AB", byteorder="big")
result_big = cmd_big.encode()
# Result: b"WR DM100 16706\r\n"
```


## Supported Commands

### Read Commands
- **Single Read**: `RD DM100\r\n` - Read one register
- **Multiple Read**: `RDS DM100 10\r\n` - Read multiple consecutive registers

### Write Commands
- **Single Write**: `WR DM100 00042\r\n` - Write single value (5-digit format)
- **Multiple Write**: `WRS DM100 5 00001 00002 00003 00004 00005\r\n` - Write multiple values (5-digit format)


## Project Structure

```
pykeyence/
├── src/pykeyence_plc_link/
│   ├── client.py          # Main PLC client implementation
│   ├── data.py            # Command builders, data structures, CharConverter utilities, and decode_plc_data_to_unicode function
│   ├── protocol.py        # UDP protocol implementation
│   ├── monitor.py         # Real-time monitoring functionality
│   ├── heartbeat.py       # Heartbeat implementation
│   └── mock/              # Mock PLC server for testing
├── examples/
│   ├── plc_client.py      # Basic client usage
│   ├── plc_monitor.py     # Monitoring example
│   └── plc_heartbeat.py   # Heartbeat example
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
    def write(self, address: str, data: Union[int, list[int]]) -> bool
```

**Methods:**
- `read(address, count=1)`: Read data from PLC register
- `write(address, data)`: Write data to PLC register (supports both integer and list of integers)

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

**Parameters:**
- `client`: PLC client instance
- `address`: Register address to monitor
- `count`: Number of registers to monitor
- `polling_interval_ms`: Polling interval in milliseconds
- `on_changed_callback`: Callback function when value changes
- `on_disconnected_callback`: Callback function when connection is lost

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

**Parameters:**
- `client`: PLC client instance
- `address`: Register address for heartbeat
- `interval_ms`: Heartbeat interval in milliseconds
- `on_disconnected_callback`: Callback function when connection is lost

### CharConverter

```python
class CharConverter:
    @staticmethod
    def string_to_16bit_decimal(data: str, byteorder: str = "little") -> str
    @staticmethod
    def decimal_16bit_to_string(data: int) -> str
```

**Methods:**
- `string_to_16bit_decimal(data, byteorder="little")`: Convert string to 16-bit decimal (returns 5-digit formatted string)
- `decimal_16bit_to_string(data)`: Convert 16-bit decimal to string

### decode_plc_data_to_unicode

```python
def decode_plc_data_to_unicode(data_list: list[str], byteorder: str = "little") -> str
```

**Parameters:**
- `data_list`: List of 5-digit number strings from PLC (e.g., ["00086", "00049"])
- `byteorder`: Byte order ("little" or "big"), defaults to "little"

**Returns:**
- Parsed unicode string from PLC data

### WriteCommand

```python
@dataclass
class WriteCommand:
    address: str
    data: str
    cr: str = "\r\n"
    byteorder: str = "little"
    
    def encode(self) -> bytes
```

**Features:**
- Automatic zero-padding for odd-length data
- Support for both little and big endian
- Single and multiple data write support
- PLC-compatible 5-digit data formatting

### ReadCommand

```python
@dataclass
class ReadCommand:
    address: str
    count: int = 1
    
    def encode(self) -> bytes
```

### ReceivedData

```python
@dataclass
class ReceivedData:
    data: bytes
    
    def decode(self) -> str
```


## Complete Examples

### Basic Client Usage

```python
from pykeyence_plc_link.client import KeyencePlcClient
from pykeyence_plc_link.mock.mock_keyence_plc_server import MockKeyencePlcServer
import time

# Start mock server for testing
mock_server = MockKeyencePlcServer(ip="127.0.0.1", port=8501)
mock_server.start()
time.sleep(1)

# Create client
client = KeyencePlcClient(host="127.0.0.1", port=8501)

# Write and read data (now supports integers directly)
value = 42
client.write("DM100", value)
print(f"Wrote value '{value}' to DM100.")

res = client.read("DM100")
print(f"Read value from DM100: {res}")

# Write multiple values
values = [100, 200, 300]
client.write("DM100", values)
print(f"Wrote multiple values to DM100: {values}")

# Cleanup
mock_server.stop()
```


### Real-time Monitoring

```python
import time
from pykeyence_plc_link.mock.mock_keyence_plc_server import MockKeyencePlcServer
from pykeyence_plc_link.client import KeyencePlcClient
from pykeyence_plc_link.monitor import PlcMonitor

# Start mock server
mock_server = MockKeyencePlcServer(ip="127.0.0.1", port=8501)
mock_server.start()
time.sleep(1)

def on_status_changed(new_value: str):
    print(f"PLC 상태 변경 감지: {new_value}")

def on_disconnected():
    print("PLC와의 연결이 끊어졌습니다.")

# Create client and monitor
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

# Simulate value changes
mock_server.memory["DM100"] = "00000"
time.sleep(1)
mock_server.memory["DM100"] = "00042"
time.sleep(1)

# Cleanup
mock_server.stop()
monitor.stop()
```


### Heartbeat Implementation

```python
import time
from pykeyence_plc_link.mock.mock_keyence_plc_server import MockKeyencePlcServer
from pykeyence_plc_link.client import KeyencePlcClient
from pykeyence_plc_link.heartbeat import Heartbeat

# Start mock server
mock_server = MockKeyencePlcServer(ip="127.0.0.1", port=8501)
mock_server.start()
time.sleep(1)

# Create client and heartbeat
client = KeyencePlcClient(host="127.0.0.1", port=8501)

heartbeat = Heartbeat(
    client=client,
    address="DM100",
    interval_ms=1000
)
heartbeat.start()

# Monitor heartbeat for 5 seconds
start_time = time.time()
while time.time() - start_time < 5:
    time.sleep(0.1)
    print(f"Heartbeat value: {mock_server.memory['DM100']}")

# Cleanup
heartbeat.stop()
mock_server.stop()
```


### Advanced Data Handling with New Features

```python
from pykeyence_plc_link.data import WriteCommand, ReadCommand, CharConverter, decode_plc_data_to_unicode

# Create commands manually
write_cmd = WriteCommand(address="DM100", data="ABC", byteorder="little")
read_cmd = ReadCommand(address="DM100", count=5)

# Encode commands
write_bytes = write_cmd.encode()
read_bytes = read_cmd.encode()

print(f"Write command: {write_bytes}")
print(f"Read command: {read_bytes}")

# Use CharConverter for custom conversions
decimal_value = CharConverter.string_to_16bit_decimal("XY", "big")
string_value = CharConverter.decimal_16bit_to_string(decimal_value)

print(f"XY -> {decimal_value} -> {string_value}")

# Example: Process BCR data step by step
bcr_chars = ["V1", "43", "-0", "00", "43", "B/", "24", "05", "10", "/0", "00", "64"]
encoded_data = [CharConverter.string_to_16bit_decimal(char) for char in bcr_chars]
print(f"Encoded BCR data: {encoded_data}")

# Parse PLC continuous data into unicode string
plc_data = ['12662', '13108', '12333', '12336', '13108', '12098', '13362', '13616', '12337', '12335', '12336', '13366']
parsed_string = decode_plc_data_to_unicode(plc_data, byteorder="little")
print(f"Parsed BCR data: {parsed_string}")

# Parse back to string
decoded_string = decode_plc_data_to_unicode(encoded_data, byteorder="little")
print(f"Decoded BCR string: {decoded_string}")
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
from pykeyence_plc_link.mock.mock_keyence_plc_server import MockKeyencePlcServer

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
- **Default Byte Order**: Little endian
- **Auto-padding**: Odd-length data automatically padded with '0'
- **PLC Data Format**: 5-digit zero-padded strings (e.g., "00001", "00100")

### PLC Address Format
- **DM Registers**: `DM100`, `DM200`, etc.
- **Other registers**: Follow Keyence naming convention

### Data Conversion Settings
- **String Length**: Must be 2 characters or less for direct conversion
- **Auto-padding**: Single characters and odd-length strings automatically padded
- **Endian Support**: Both little and big endian byte orders supported
- **PLC Format**: Data automatically formatted as 5-digit strings for PLC compatibility


## Protocol Details

This library implements the Keyence ASCII protocol over UDP:

- Commands end with `\r\n` (CRLF)
- Responses are ASCII encoded
- Success responses start with data or "OK"
- Error responses start with "E" followed by error code
- Data is automatically converted between ASCII strings and 16-bit decimal values
- PLC data is formatted as 5-digit zero-padded strings for compatibility

### Data Processing Flow

1. **Input Validation**: Check data length and format
2. **Auto-padding**: Add '0' to odd-length data
3. **Conversion**: Convert 2-character chunks to 16-bit decimal
4. **PLC Formatting**: Format data as 5-digit strings for PLC compatibility
5. **Command Generation**: Create appropriate PLC command
6. **Transmission**: Send command via UDP
7. **Response Processing**: Handle PLC response and convert back to string

### Error Handling

- **Invalid String Length**: Raises `ValueError` for strings longer than 2 characters in direct conversion
- **Invalid Byte Order**: Raises `ValueError` for unsupported endian values
- **Network Errors**: Handled gracefully with timeout and retry mechanisms
- **PLC Errors**: Parsed and reported through client methods
- **Data Format Errors**: Validates 5-digit format for PLC data


## Requirements

- Python 3.8+
- No external dependencies for core functionality
- pytest, pytest-cov, pytest-mock for development


## Release Notes

### Version 0.1.9 (Latest)
- **Major Data Handling Improvements**: Enhanced PLC data compatibility with 5-digit formatting
- **Class Renaming**: `TwoCharConverter` → `CharConverter` for better clarity
- **New Utility Function**: Added `decode_plc_data_to_unicode` for parsing PLC continuous data
- **Enhanced Client Interface**: Client now supports both integer and list of integers for write operations
- **Improved Data Processing**: Better separation of string parsing and data conversion logic
- **PLC Format Support**: Automatic conversion to PLC-compatible 5-digit string format
- **Better Error Handling**: Enhanced validation for data format and conversion operations

### Version 0.1.5
- Added DataConverter utility class for data conversion
- Improved data handling with automatic zero-padding
- Enhanced endian support for both little and big endian
- Better separation of concerns between data classes and conversion logic
- Comprehensive test coverage for all new features

### Version 0.1.0
- Initial release
- Basic PLC communication
- Monitoring and heartbeat functionality
- Mock server for testing