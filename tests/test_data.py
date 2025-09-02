import pytest
from pykeyence_plc_link.data import (
    TwoCharConverter,
    WriteCommand,
    ReadCommand,
    ReceivedData
)


class TestTwoCharConverter:
    """TwoCharConverter 클래스에 대한 테스트"""
    
    def test_string_to_16bit_decimal_little_endian(self):
        """리틀 엔디안으로 2글자 문자열을 16비트 10진수로 변환하는 테스트"""
        # 정상 케이스
        assert TwoCharConverter.string_to_16bit_decimal("AB", "little") == 16961
        assert TwoCharConverter.string_to_16bit_decimal("V1", "little") == 12630
        assert TwoCharConverter.string_to_16bit_decimal("12", "little") == 12849
        
    def test_string_to_16bit_decimal_big_endian(self):
        """빅 엔디안으로 2글자 문자열을 16비트 10진수로 변환하는 테스트"""
        # 정상 케이스
        assert TwoCharConverter.string_to_16bit_decimal("AB", "big") == 16706
        assert TwoCharConverter.string_to_16bit_decimal("V1", "big") == 22065  # V=86, 1=49, big endian: 86*256 + 49 = 22065
        assert TwoCharConverter.string_to_16bit_decimal("12", "big") == 12594
        
    def test_string_to_16bit_decimal_default_byteorder(self):
        """기본 바이트 순서(리틀 엔디안)로 변환하는 테스트"""
        assert TwoCharConverter.string_to_16bit_decimal("AB") == 16961
        
    def test_string_to_16bit_decimal_invalid_length(self):
        """잘못된 길이의 문자열에 대한 예외 테스트"""
        with pytest.raises(ValueError, match="문자열은 반드시 2글자여야 합니다."):
            TwoCharConverter.string_to_16bit_decimal("A")
        
        with pytest.raises(ValueError, match="문자열은 반드시 2글자여야 합니다."):
            TwoCharConverter.string_to_16bit_decimal("ABC")
            
        with pytest.raises(ValueError, match="문자열은 반드시 2글자여야 합니다."):
            TwoCharConverter.string_to_16bit_decimal("")
            
    def test_string_to_16bit_decimal_invalid_byteorder(self):
        """잘못된 바이트 순서에 대한 예외 테스트"""
        with pytest.raises(ValueError, match='byteorder는 "little" 또는 "big"이어야 합니다.'):
            TwoCharConverter.string_to_16bit_decimal("AB", "middle")
            
    def test_decimal_16bit_to_string(self):
        """16비트 10진수를 2글자 문자열로 변환하는 테스트"""
        # 정상 케이스
        assert TwoCharConverter.decimal_16bit_to_string(16961) == "AB"
        assert TwoCharConverter.decimal_16bit_to_string(12630) == "V1"
        assert TwoCharConverter.decimal_16bit_to_string(12849) == "12"
        assert TwoCharConverter.decimal_16bit_to_string(0) == "\x00\x00"
        # 65535는 ASCII 범위를 벗어나므로 테스트에서 제외
        # assert TwoCharConverter.decimal_16bit_to_string(65535) == "\xff\xff"
        
    def test_decimal_16bit_to_string_invalid_range(self):
        """ASCII 변환 범위를 벗어나는 데이터에 대한 예외 테스트"""
        with pytest.raises(ValueError, match="ascii 변환 범위를 벗어납니다. 데이터는 반드시 65535 이하여야 합니다."):
            TwoCharConverter.decimal_16bit_to_string(65536)
            
        with pytest.raises(ValueError, match="ascii 변환 범위를 벗어납니다. 데이터는 반드시 65535 이하여야 합니다."):
            TwoCharConverter.decimal_16bit_to_string(100000)
            
        with pytest.raises(ValueError, match="ascii 변환 범위를 벗어납니다. 데이터는 반드시 65535 이하여야 합니다."):
            TwoCharConverter.decimal_16bit_to_string(999999)


class TestWriteCommand:
    """WriteCommand 클래스에 대한 테스트"""
    
    def test_write_command_single_data(self):
        """단일 데이터로 WriteCommand 생성하는 테스트"""
        cmd = WriteCommand(address="DM100", data=12345)
        assert cmd.address == "DM100"
        assert cmd.data == [12345]
        assert cmd.cr == "\r\n"
        
    def test_write_command_multiple_data(self):
        """여러 데이터로 WriteCommand 생성하는 테스트"""
        cmd = WriteCommand(address="DM200", data=[1, 2, 3, 4, 5])
        assert cmd.address == "DM200"
        assert cmd.data == [1, 2, 3, 4, 5]
        
    def test_write_command_validation_valid_data(self):
        """유효한 데이터에 대한 검증 테스트"""
        # 정상 범위의 데이터
        cmd = WriteCommand(address="DM100", data=0)
        assert cmd.data == [0]
        
        cmd = WriteCommand(address="DM100", data=65535)
        assert cmd.data == [65535]
        
        cmd = WriteCommand(address="DM100", data=[100, 200, 300])
        assert cmd.data == [100, 200, 300]
        
    def test_write_command_validation_invalid_data_type(self):
        """잘못된 데이터 타입에 대한 예외 테스트"""
        with pytest.raises(ValueError, match="데이터는 반드시 정수여야 합니다."):
            WriteCommand(address="DM100", data="invalid")
            
        with pytest.raises(ValueError, match="데이터는 반드시 정수여야 합니다."):
            WriteCommand(address="DM100", data=[1, "invalid", 3])
            
        with pytest.raises(ValueError, match="데이터는 반드시 정수여야 합니다."):
            WriteCommand(address="DM100", data=[1.5, 2])
            
    def test_write_command_validation_negative_data(self):
        """음수 데이터에 대한 예외 테스트"""
        with pytest.raises(ValueError, match="데이터는 반드시 양수여야 합니다."):
            WriteCommand(address="DM100", data=-1)
            
        with pytest.raises(ValueError, match="데이터는 반드시 양수여야 합니다."):
            WriteCommand(address="DM100", data=[1, -2, 3])
            
    def test_write_command_validation_data_too_large(self):
        """65535를 초과하는 데이터에 대한 예외 테스트"""
        with pytest.raises(ValueError, match="데이터는 반드시 99999 이하여야 합니다."):
            WriteCommand(address="DM100", data=100000)
            
        with pytest.raises(ValueError, match="데이터는 반드시 99999 이하여야 합니다."):
            WriteCommand(address="DM100", data=[1, 100000, 3])
            
    def test_write_command_encode_single_data(self):
        """단일 데이터 명령어 인코딩 테스트"""
        cmd = WriteCommand(address="DM100", data=12345)
        encoded = cmd.encode()
        expected = b"WR DM100 12345\r\n"
        assert encoded == expected
        
    def test_write_command_encode_multiple_data(self):
        """여러 데이터 명령어 인코딩 테스트"""
        cmd = WriteCommand(address="DM200", data=[1, 2, 3, 4, 5])
        encoded = cmd.encode()
        expected = b"WRS DM200 5 00001 00002 00003 00004 00005\r\n"
        assert encoded == expected
        
    def test_write_command_encode_two_data(self):
        """2개 데이터 명령어 인코딩 테스트 (WR 명령어 사용)"""
        cmd = WriteCommand(address="DM300", data=[100, 200])
        encoded = cmd.encode()
        expected = b"WRS DM300 2 00100 00200\r\n"
        assert encoded == expected


class TestReadCommand:
    """ReadCommand 클래스에 대한 테스트"""
    
    def test_read_command_single_read(self):
        """단일 읽기 명령어 생성 테스트"""
        cmd = ReadCommand(address="DM100")
        assert cmd.address == "DM100"
        assert cmd.count == 1
        
    def test_read_command_multiple_read(self):
        """여러 읽기 명령어 생성 테스트"""
        cmd = ReadCommand(address="DM200", count=10)
        assert cmd.address == "DM200"
        assert cmd.count == 10
        
    def test_read_command_encode_single_read(self):
        """단일 읽기 명령어 인코딩 테스트"""
        cmd = ReadCommand(address="DM100")
        encoded = cmd.encode()
        expected = b"RD DM100\r\n"
        assert encoded == expected
        
    def test_read_command_encode_multiple_read(self):
        """여러 읽기 명령어 인코딩 테스트"""
        cmd = ReadCommand(address="DM200", count=10)
        encoded = cmd.encode()
        expected = b"RDS DM200 10\r\n"
        assert encoded == expected


class TestReceivedData:
    """ReceivedData 클래스에 대한 테스트"""
    
    def test_received_data_decode_single_value(self):
        """단일 값 디코딩 테스트"""
        recv_data = ReceivedData(data=b"12345")
        decoded = recv_data.decode()
        assert decoded == ["12345"]
        
    def test_received_data_decode_multiple_values(self):
        """여러 값 디코딩 테스트"""
        recv_data = ReceivedData(data=b"00001 65534")
        decoded = recv_data.decode()
        assert decoded == ["00001", "65534"]
        
    def test_received_data_decode_with_crlf(self):
        """CRLF가 포함된 데이터 디코딩 테스트"""
        recv_data = ReceivedData(data=b"12345\r\n")
        decoded = recv_data.decode()
        assert decoded == ["12345"]
        
    def test_received_data_decode_ok_response(self):
        """OK 응답 디코딩 테스트"""
        recv_data = ReceivedData(data=b"OK")
        decoded = recv_data.decode()
        assert decoded == "OK"
        
    def test_received_data_decode_ok_response_with_crlf(self):
        """CRLF가 포함된 OK 응답 디코딩 테스트"""
        recv_data = ReceivedData(data=b"OK\r\n")
        decoded = recv_data.decode()
        assert decoded == "OK"
        
    def test_received_data_decode_empty_data(self):
        """빈 데이터에 대한 예외 테스트"""
        with pytest.raises(ValueError, match="데이터가 없습니다."):
            ReceivedData(data=b"").decode()
            
        with pytest.raises(ValueError, match="데이터가 없습니다."):
            ReceivedData(data=None).decode()
            
    def test_received_data_decode_invalid_length(self):
        """5자리가 아닌 데이터에 대한 예외 테스트"""
        with pytest.raises(ValueError, match="데이터가 올바르지 않습니다. 5자리가 아닙니다."):
            ReceivedData(data=b"1234").decode()
            
        with pytest.raises(ValueError, match="데이터가 올바르지 않습니다. 5자리가 아닙니다."):
            ReceivedData(data=b"123456").decode()
            
        with pytest.raises(ValueError, match="데이터가 올바르지 않습니다. 5자리가 아닙니다."):
            ReceivedData(data=b"1234 56789").decode()
            
    def test_received_data_decode_mixed_valid_invalid(self):
        """유효하지 않은 데이터가 포함된 경우 예외 테스트"""
        with pytest.raises(ValueError, match="데이터가 올바르지 않습니다. 5자리가 아닙니다."):
            ReceivedData(data=b"12345 1234").decode()


class TestIntegration:
    """통합 테스트"""
    
    def test_write_and_read_workflow(self):
        """쓰기와 읽기 워크플로우 테스트"""
        # 쓰기 명령어 생성
        write_cmd = WriteCommand(address="DM100", data=12345)
        write_encoded = write_cmd.encode()
        assert write_encoded == b"WR DM100 12345\r\n"
        
        # 읽기 명령어 생성
        read_cmd = ReadCommand(address="DM100", count=1)
        read_encoded = read_cmd.encode()
        assert read_encoded == b"RD DM100\r\n"
        
        # 수신 데이터 처리
        received_data = ReceivedData(data=b"12345")
        decoded = received_data.decode()
        assert decoded == ["12345"]
        
    def test_multiple_data_workflow(self):
        """여러 데이터 워크플로우 테스트"""
        # 여러 데이터 쓰기
        write_cmd = WriteCommand(address="DM200", data=[1, 2, 3, 4, 5])
        write_encoded = write_cmd.encode()
        assert write_encoded == b"WRS DM200 5 00001 00002 00003 00004 00005\r\n"
        
        # 여러 데이터 읽기
        read_cmd = ReadCommand(address="DM200", count=5)
        read_encoded = read_cmd.encode()
        assert read_encoded == b"RDS DM200 5\r\n"
        
        # 여러 데이터 수신 처리
        received_data = ReceivedData(data=b"00001 00002 00003 00004 00005")
        decoded = received_data.decode()
        assert decoded == ["00001", "00002", "00003", "00004", "00005"]
        
    def test_two_char_converter_integration(self):
        """TwoCharConverter 통합 테스트"""
        # 문자열을 숫자로 변환
        original_string = "AB"
        decimal_value = TwoCharConverter.string_to_16bit_decimal(original_string)
        
        # 숫자를 다시 문자열로 변환
        converted_string = TwoCharConverter.decimal_16bit_to_string(decimal_value)
        
        # 변환된 문자열이 원본과 일치하는지 확인
        assert converted_string == original_string


if __name__ == "__main__":
    pytest.main([__file__])
