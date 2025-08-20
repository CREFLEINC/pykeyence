
"""
키엔스 매뉴얼을 참고하여 명령어 포맷을 작성하였습니다.

* 1자리 읽기 : 명령어 + 공백 + 주소 + CRLF                   
           -> "RD DM100\r\n" 

* 10자리 읽기 : 명령어 + 공백 + 주소 + 공백 + 길이 + CRLF      
           -> "RDS DM100 10\r\n"

* 1자리 쓰기 :  명령어 + 공백 + 주소 + 공백 + 데이터 + CRLF                                           
           -> "WR DM100 1\r\n" 

* 10자리 쓰기 : 명령어 + 공백 + 주소 + 공백 + 길이 + 공백 + 데이터 + 공백 + ... + 공백 + 데이터 + CRLF     
            -> "WRS DM100 10 01 02 03 04 05 06 07 08 09 10\r\n"
"""


from dataclasses import dataclass


@dataclass
class WriteCommand:
    address: str
    data: str
    cr: str = "\r\n"

    def encode(self) -> bytes:
        if len(self.data) > 2:
            _data_list = list(self.data[i:i+2] for i in range(0, len(self.data), 2))
            command_format = f"WRS {self.address} {len(_data_list)} {' '.join(_data_list)}{self.cr}"
        else:
            command_format = f"WR {self.address} {self.data}{self.cr}"

        return command_format.encode('ascii')
        
        
@dataclass
class ReadCommand:
    address: str
    count: int = 1

    def encode(self) -> bytes:
        if self.count > 1:
            command_format = f"RDS {self.address} {self.count}\r\n"
        else:
            command_format = f"RD {self.address}\r\n"

        return command_format.encode('ascii')
    

@dataclass
class ReceivedData:
    data: bytes

    def decode(self) -> str:
        return self.data.decode('ascii')


if __name__ == "__main__":
    # Example usage
    write_cmd = WriteCommand(address="DM100", data="12345")
    print(write_cmd.encode())

    read_cmd = ReadCommand(address="DM100", count=1)
    print(read_cmd.encode())