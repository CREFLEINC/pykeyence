
"""
키엔스 매뉴얼을 참고하여 명령어 포맷을 작성하였습니다.

* 1자리 읽기 : 명령어 + 공백 + 주소 + CRLF                   
           -> "RD DM100\r\n" 

* 10자리 읽기 : 명령어 + 공백 + 주소 + 공백 + 길이 + CRLF      
           -> "RDS DM100 10\r\n"

* 1자리 쓰기 :  명령어 + 공백 + 주소 + 공백 + 데이터 + CRLF                                           
           -> "WR DM100 12345\r\n" 

* 10자리 쓰기 : 명령어 + 공백 + 주소 + 공백 + 길이 + 공백 + 데이터 + 공백 + ... + 공백 + 데이터 + CRLF     
            -> "WRS DM100 6 12345 67890 12345 67890 12345 67890\r\n"
"""

from dataclasses import dataclass
from typing import Union


class TwoCharConverter:
    """
    PLC에서 BCR 문자열을 받을 때 사용하는 데이터 변환 유틸리티 클래스
    
    PLC에서 BCR 문자열을 받으면 address 하나당 문자열 두 개를 보관함.
    해당 문자열을 읽으면 리틀인디언 방식으로 인코딩된 5자리 숫자가 넘어옴.
    따라서 해석가능한 문자열로 변환하기 위해서 해당 클래스가 필요함.
    
    주요 기능:
    - 2글자 문자열을 16비트 10진수로 변환 (string_to_16bit_decimal)
    - 16비트 10진수를 2글자 문자열로 변환 (decimal_16bit_to_string)
    """
    
    @staticmethod
    def string_to_16bit_decimal(data: str, byteorder: str = "little") -> int:
        """
        문자열(2글자)을 16비트 10진수로 변환
        
        Args:
            data: 변환할 2글자 문자열
            byteorder: 바이트 순서 ("little" 또는 "big"), 기본값은 "little"
            
        Returns:
            변환된 10진수
            
        Raises:
            ValueError: 문자열이 2글자가 아닌 경우
            
        예) "AB" -> 16961 (little), 16706 (big)
            "V1" -> 12630 (little), 12849 (big)
        """
        if len(data) != 2:
            raise ValueError("문자열은 반드시 2글자여야 합니다.")
        
        if byteorder not in ["little", "big"]:
            raise ValueError('byteorder는 "little" 또는 "big"이어야 합니다.')
            
        return int.from_bytes(data.encode("ascii"), byteorder)
    
    @staticmethod
    def decimal_16bit_to_string(data: int) -> str:
        """
        16비트 10진수를 문자열로 변환
        
        Args:
            data: 변환할 10진수
            
        Returns:
            변환된 2글자 문자열
        """
        if data > 65535:
            raise ValueError(f"ascii 변환 범위를 벗어납니다. 데이터는 반드시 65535 이하여야 합니다. {data}")
        return data.to_bytes(2, 'little').decode("ascii")


@dataclass
class WriteCommand:
    address: str
    data: Union[int, list[int]]
    cr: str = "\r\n"

    def __post_init__(self):
        if not isinstance(self.data, list):
            self.data = [self.data]

        self.validate()

    def validate(self):        
        for data in self.data:
            if not isinstance(data, int):
                raise ValueError(f"데이터는 반드시 정수여야 합니다. {data}")
            if data < 0:
                raise ValueError(f"데이터는 반드시 양수여야 합니다. {data}")
            if data > 99999:
                raise ValueError(f"데이터는 반드시 99999 이하여야 합니다. {data}")

    def encode(self) -> bytes:        
        if len(self.data) > 1:
            command_format = f"WRS {self.address} {len(self.data)} {' '.join(str(d).zfill(5) for d in self.data)}{self.cr}"
        else:
            command_format = f"WR {self.address} {str(self.data[0]).zfill(5)}{self.cr}"

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
    cr: str = "\r\n"

    def decode(self) -> list[str]:
        if not self.data:
            raise ValueError("데이터가 없습니다.")

        decoded_data = self.data.decode('ascii')
        if decoded_data.startswith('OK'):
            # CRLF 제거
            if decoded_data.endswith(self.cr):
                return decoded_data[:-2]
            return decoded_data
        
        _data_list = decoded_data.split(' ')
        _new_data_list = []
        for item in _data_list:
            if item.endswith(self.cr):
                item = item[:-2]
            
            if len(item) != 5:
                raise ValueError(f"데이터가 올바르지 않습니다. 5자리가 아닙니다. {item}")

            _new_data_list.append(item)
        
        return _new_data_list


if __name__ == "__main__":
    # Example usage    
    wr_cmd = WriteCommand(address="DM100", data=100)
    print('1', wr_cmd.encode())

    wr_cmd = WriteCommand(address="DM100", data=[1, 2, 3, 4, 5])
    print('2', wr_cmd.encode())

    rd_cmd = ReadCommand(address="DM100", count=1)
    print('3', rd_cmd.encode())

    rd_cmd = ReadCommand(address="DM100", count=10)
    print('4', rd_cmd.encode())

    recv_bytes = b'12345'
    recv_data = ReceivedData(data=recv_bytes)
    print('5', recv_data.decode())

    recv_bytes = b'00001 65534'
    recv_data = ReceivedData(data=recv_bytes)
    values = recv_data.decode()
    print('6', values)

    word = 'AB'
    print('7', TwoCharConverter.string_to_16bit_decimal(word))

    word = 16961
    print('8', TwoCharConverter.decimal_16bit_to_string(word))