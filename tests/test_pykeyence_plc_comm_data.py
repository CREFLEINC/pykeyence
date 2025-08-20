import pytest
from src.pykeyence_plc_comm.data import WriteCommand, ReadCommand


@pytest.mark.parametrize("address, data, expected", [
    ("DM100", "01", b"WR DM100 01\r\n"),
    ("DM100", "123456789", b"WRS DM100 5 12 34 56 78 9\r\n"),  # TODO : 키엔스 장비와 테스트가 필요함..! 마지막에 한자리인 경우 0을 붙여야할지?????
])
def test_write_command(address, data, expected):
    command = WriteCommand(address=address, data=data)
    assert command.encode() == expected 


@pytest.mark.parametrize("address, count, expected", [
    ("DM100", 1, b"RD DM100\r\n"),
    ("DM100", 10, b"RDS DM100 10\r\n"),
])
def test_read_command(address, count, expected):
    command = ReadCommand(address=address, count=count)
    assert command.encode() == expected 
