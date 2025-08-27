import pytest
from pykeyence_plc_link.data import WriteCommand, ReadCommand, ReceivedData, DataConverter


class TestDataConverter:
    """DataConverter 유틸리티 클래스 테스트"""
    
    def test_string_to_16bit_decimal_little_endian(self):
        """little endian으로 2글자 문자열을 16비트 10진수로 변환"""
        # "AB" -> little endian: 0x4241 = 16961
        result = DataConverter.string_to_16bit_decimal("AB", "little")
        assert result == 16961
        
        # "V1" -> little endian: 0x3156 = 12630
        result = DataConverter.string_to_16bit_decimal("V1", "little")
        assert result == 12630
    
    def test_string_to_16bit_decimal_big_endian(self):
        """big endian으로 2글자 문자열을 16비트 10진수로 변환"""
        # "AB" -> big endian: 0x4142 = 16706
        result = DataConverter.string_to_16bit_decimal("AB", "big")
        assert result == 16706
        
        # "V1" -> big endian: 0x5631 = 22065
        result = DataConverter.string_to_16bit_decimal("V1", "big")
        assert result == 22065
    
    def test_string_to_16bit_decimal_default_little(self):
        """기본값은 little endian"""
        result = DataConverter.string_to_16bit_decimal("AB")  # byteorder 생략
        assert result == 16961  # little endian 결과
    
    def test_string_to_16bit_decimal_invalid_length(self):
        """2글자가 아닌 문자열 입력 시 ValueError 발생"""
        with pytest.raises(ValueError, match="문자열은 반드시 2글자여야 합니다."):
            DataConverter.string_to_16bit_decimal("A")  # 1글자
        
        with pytest.raises(ValueError, match="문자열은 반드시 2글자여야 합니다."):
            DataConverter.string_to_16bit_decimal("ABC")  # 3글자
    
    def test_string_to_16bit_decimal_invalid_byteorder(self):
        """잘못된 byteorder 입력 시 ValueError 발생"""
        with pytest.raises(ValueError, match='byteorder는 "little" 또는 "big"이어야 합니다.'):
            DataConverter.string_to_16bit_decimal("AB", "invalid")
    
    def test_string_to_16bit_decimal_edge_cases(self):
        """경계값 테스트"""
        # "00" -> little endian: 0x3030 = 12336
        result = DataConverter.string_to_16bit_decimal("00", "little")
        assert result == 12336
        
        # "ZZ" -> little endian: 0x5A5A = 23130
        result = DataConverter.string_to_16bit_decimal("ZZ", "little")
        assert result == 23130
    
    def test_decimal_16bit_to_string(self):
        """16비트 10진수를 문자열로 변환 테스트"""
        # 16961 -> "AB" (little endian)
        result = DataConverter.decimal_16bit_to_string(16961)
        assert result == "AB"
        
        # 16706 -> "BA" (little endian으로 고정)
        result = DataConverter.decimal_16bit_to_string(16706)
        assert result == "BA"
        
        # 12630 -> "V1" (little endian)
        result = DataConverter.decimal_16bit_to_string(12630)
        assert result == "V1"
    
    def test_static_methods(self):
        """정적 메서드가 올바르게 작동하는지 테스트"""
        # 인스턴스 생성 없이 직접 호출 가능
        assert DataConverter.string_to_16bit_decimal("AB") == 16961
        assert DataConverter.decimal_16bit_to_string(16961) == "AB"


class TestWriteCommand:
    """WriteCommand 클래스 테스트"""
    
    def test_write_command_initialization(self):
        """WriteCommand 초기화 테스트"""
        command = WriteCommand(address="DM100", data="AB")
        assert command.address == "DM100"
        assert command.data == "AB"
        assert command.cr == "\r\n"
        assert command.byteorder == "little"
        
        # 커스텀 값으로 초기화
        command = WriteCommand(address="DM200", data="CD", cr="\n", byteorder="big")
        assert command.address == "DM200"
        assert command.data == "CD"
        assert command.cr == "\n"
        assert command.byteorder == "big"
    
    def test_encode_single_data(self):
        """단일 데이터 쓰기 명령어 인코딩 테스트"""
        command = WriteCommand(address="DM100", data="AB")
        result = command.encode()
        expected = b"WR DM100 16961\r\n"  # "AB" -> 16961 (little endian)
        assert result == expected
        
        # big endian으로 테스트
        command = WriteCommand(address="DM100", data="AB", byteorder="big")
        result = command.encode()
        expected = b"WR DM100 16706\r\n"  # "AB" -> 16706 (big endian)
        assert result == expected
    
    def test_encode_multiple_data(self):
        """여러 데이터 쓰기 명령어 인코딩 테스트"""
        command = WriteCommand(address="DM100", data="ABCD")
        result = command.encode()
        # "AB" -> 16961, "CD" -> 17475 (little endian)
        expected = b"WRS DM100 2 16961 17475\r\n"
        assert result == expected
        
        # 홀수 길이 데이터 테스트 (자동으로 0 추가)
        command = WriteCommand(address="DM100", data="ABC")
        result = command.encode()
        # "AB" -> 16961, "C0" -> 0x3043 = 12355 (자동 0 추가 후)
        expected = b"WRS DM100 2 16961 12355\r\n"
        assert result == expected
    
    def test_encode_with_custom_cr(self):
        """커스텀 CR 문자로 인코딩 테스트"""
        command = WriteCommand(address="DM100", data="AB", cr="\n")
        result = command.encode()
        expected = b"WR DM100 16961\n"
        assert result == expected
    
    def test_encode_odd_length_data(self):
        """홀수 길이 데이터 자동 0 추가 테스트"""
        # "a" -> "a0" -> 0x3061 = 12385 (little endian)
        command = WriteCommand(address="DM100", data="a")
        result = command.encode()
        expected = b"WR DM100 12385\r\n"
        assert result == expected
        
        # "x" -> "x0" -> 0x3078 = 12408 (little endian)
        command = WriteCommand(address="DM100", data="x")
        result = command.encode()
        expected = b"WR DM100 12408\r\n"
        assert result == expected
        
        # big endian으로 테스트
        command = WriteCommand(address="DM100", data="a", byteorder="big")
        result = command.encode()
        expected = b"WR DM100 24880\r\n"  # "a0" -> 0x6130 = 24880 (big endian)
        assert result == expected


class TestReadCommand:
    """ReadCommand 클래스 테스트"""
    
    def test_read_command_initialization(self):
        """ReadCommand 초기화 테스트"""
        command = ReadCommand(address="DM100")
        assert command.address == "DM100"
        assert command.count == 1  # 기본값
        
        command = ReadCommand(address="DM200", count=5)
        assert command.address == "DM200"
        assert command.count == 5
    
    def test_encode_single_read(self):
        """단일 읽기 명령어 인코딩 테스트"""
        command = ReadCommand(address="DM100", count=1)
        result = command.encode()
        expected = b"RD DM100\r\n"
        assert result == expected
    
    def test_encode_multiple_read(self):
        """여러 읽기 명령어 인코딩 테스트"""
        command = ReadCommand(address="DM100", count=10)
        result = command.encode()
        expected = b"RDS DM100 10\r\n"
        assert result == expected
        
        command = ReadCommand(address="DM200", count=100)
        result = command.encode()
        expected = b"RDS DM200 100\r\n"
        assert result == expected
    
    def test_encode_edge_cases(self):
        """경계값 테스트"""
        # count가 1보다 큰 경우
        command = ReadCommand(address="DM100", count=2)
        result = command.encode()
        expected = b"RDS DM100 2\r\n"
        assert result == expected
        
        # count가 1인 경우
        command = ReadCommand(address="DM100", count=1)
        result = command.encode()
        expected = b"RD DM100\r\n"
        assert result == expected


class TestReceivedData:
    """ReceivedData 클래스 테스트"""
    
    def test_received_data_initialization(self):
        """ReceivedData 초기화 테스트"""
        data = b"Hello World"
        received = ReceivedData(data=data)
        assert received.data == b"Hello World"
    
    def test_decode_ok_response(self):
        """OK 응답 디코딩 테스트"""
        data = b"OK"
        received = ReceivedData(data=data)
        result = received.decode()
        expected = "OK"
        assert result == expected
    
    def test_decode_numeric_data(self):
        """숫자 데이터 디코딩 테스트"""
        # "16961 17475" -> "ABCD"
        data = b"16961 17475"
        received = ReceivedData(data=data)
        result = received.decode()
        expected = "ABCD"
        assert result == expected
    
    def test_decode_single_numeric_data(self):
        """단일 숫자 데이터 디코딩 테스트"""
        # "16961" -> "AB"
        data = b"16961"
        received = ReceivedData(data=data)
        result = received.decode()
        expected = "AB"
        assert result == expected
    
    def test_decode_empty_data(self):
        """빈 데이터 디코딩 테스트"""
        received = ReceivedData(data=b"")
        result = received.decode()
        expected = ""
        assert result == expected
    
    def test_decode_none_data(self):
        """None 데이터 디코딩 테스트"""
        received = ReceivedData(data=None)
        result = received.decode()
        expected = ""


class TestIntegration:
    """통합 테스트"""
    
    def test_write_and_read_commands_together(self):
        """쓰기와 읽기 명령어를 함께 사용하는 테스트"""
        # 쓰기 명령어 생성
        write_cmd = WriteCommand(address="DM100", data="AB")
        write_bytes = write_cmd.encode()
        
        # 읽기 명령어 생성
        read_cmd = ReadCommand(address="DM100", count=1)
        read_bytes = read_cmd.encode()
        
        # 두 명령어가 모두 올바르게 생성되었는지 확인
        assert write_bytes == b"WR DM100 16961\r\n"
        assert read_bytes == b"RD DM100\r\n"
    
    def test_different_byteorders(self):
        """다양한 byteorder 설정 테스트"""
        # little endian
        cmd_little = WriteCommand(address="DM100", data="AB", byteorder="little")
        result_little = cmd_little.encode()
        assert result_little == b"WR DM100 16961\r\n"
        
        # big endian
        cmd_big = WriteCommand(address="DM100", data="AB", byteorder="big")
        result_big = cmd_big.encode()
        assert result_big == b"WR DM100 16706\r\n"
        
        # 결과가 다른지 확인
        assert result_little != result_big
    
    def test_odd_length_data_handling(self):
        """홀수 길이 데이터 처리 테스트"""
        # 홀수 길이 데이터는 자동으로 0이 추가됨
        command = WriteCommand(address="DM100", data="A")
        result = command.encode()
        # "A" -> "A0" -> 0x3041 = 12353
        expected = b"WR DM100 12353\r\n"
        assert result == expected
        
        # 3글자 데이터
        command = WriteCommand(address="DM100", data="ABC")
        result = command.encode()
        # "ABC" -> "ABC0" -> ["AB", "C0"] -> [16961, 12355]
        expected = b"WRS DM100 2 16961 12355\r\n"
        assert result == expected
    
    def test_data_converter_integration(self):
        """DataConverter와 다른 클래스들의 통합 테스트"""
        # WriteCommand에서 DataConverter 사용
        write_cmd = WriteCommand(address="DM100", data="AB")
        encoded = write_cmd.encode()
        assert encoded == b"WR DM100 16961\r\n"
        
        # ReceivedData에서 DataConverter 사용
        received = ReceivedData(data=b"16961")
        decoded = received.decode()
        assert decoded == "AB"
        
        # DataConverter 직접 사용
        decimal_value = DataConverter.string_to_16bit_decimal("AB")
        string_value = DataConverter.decimal_16bit_to_string(decimal_value)
        assert string_value == "AB"
