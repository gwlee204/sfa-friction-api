def status_return(code: int, error: bool, ret='', error_msg=''):
    """API의 결과를 입력받아 response를 만드는 함수

    Args:
        code (int): API 결과 코드
        error (bool): 에러의 유무
        ret (str, optional): 리턴할 값. Defaults to ''.
        error_msg (str, optional): 에러메세지. Defaults to ''.

    Returns:
        dict: 입력받은 인자들로부터 dictionary 타입의 object를 만들고 리턴한다.
    """
    return {
            "status-code": code,
            "error": error,
            "error-msg": error_msg,
            "return": ret
        }


def get_error_msg(code: int):
    """에러 코드를 바탕으로 에러 메세지를 출력하는 함수

    Args:
        code (int): 에러 코드

    Returns:
        str: 에러 코드에 대한 메세지를 리턴한다.
    """
    ERROR_MSG = {   # 에러 메세지 dictionary. key(int)에는 에러 코드가, value(str)에는 에러 메세지가 포함된다.
        1000: "Upload 디렉토리에 파일 없음",
        1001: "Main 함수 에러, Upload 디렉토리 패스 확인 필요",
        2000: "Upload 에러, 업로드된 파일의 데이터를 읽을 수 없음",
        2001: "Upload 에러, 업로드된 파일과 동일한 이름의 파일이 있음",
        2002: "Upload 에러, 업로드된 파일의 형식이 csv가 아님",
        2003: "Upload 에러, 업로드된 파일을 저장할 수 없음",
    }

    return ERROR_MSG[code]


def status(code: int, ret=''):
    """API의 response를 리턴하는 함수.
    code 규칙 정리 : status_code.md

    Args:
        code (int): 결과 코드
        ret (_type_): 리턴할 object

    Returns:
        dict: 입력받은 결과를 바탕으로 response를 출력한다.
    """
    if code == 200:
        return status_return(200, False, ret=ret)
    else:
        return status_return(code, True, error_msg=get_error_msg(code))