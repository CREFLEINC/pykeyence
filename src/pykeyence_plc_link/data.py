
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


class DataConverter:
    """데이터 변환을 위한 유틸리티 클래스"""
    
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
        return data.to_bytes(2, 'little').decode("ascii")


@dataclass
class WriteCommand:
    address: str
    data: str
    cr: str = "\r\n"
    byteorder: str = "little"  # little or big

    def encode(self) -> bytes:
        if len(self.data) % 2 == 1:
            self.data = self.data + "0"  # TODO : 한자리 처리방식에 대해서는 실제 PLC 확인 필요

        if len(self.data) > 2:
            _data_list = list(self.data[i:i+2] for i in range(0, len(self.data), 2))
            _data_list = list(str(DataConverter.string_to_16bit_decimal(data, self.byteorder)) for data in _data_list)
            command_format = f"WRS {self.address} {len(_data_list)} {' '.join(_data_list)}{self.cr}"
        else:
            command_format = f"WR {self.address} {DataConverter.string_to_16bit_decimal(self.data, self.byteorder)}{self.cr}"

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
        if not self.data:
            return ""
        
        decoded_data = self.data.decode('ascii')
        if decoded_data.startswith('OK'):
            return decoded_data
        
        _data_list = decoded_data.split(' ')
        _data_list = list(DataConverter.decimal_16bit_to_string(int(item)) for item in _data_list)
        return ''.join(_data_list)


if __name__ == "__main__":
    # Example usage
    word = "V1"
    print('0', word)

    write_cmd = WriteCommand(address="DM100", data=word)
    encoded_data = write_cmd.encode()
    print('1', encoded_data)

    recv_bytes = DataConverter.string_to_16bit_decimal(word)
    print('2', recv_bytes)

    recv_data = ReceivedData(data=str(recv_bytes).encode('ascii'))
    print('3', recv_data.decode())



