from fastapi import HTTPException, status


class CustomException(HTTPException):
    """自定义异常基类"""
    def __init__(self, status_code: int, detail: str, code: int = None):
        super().__init__(status_code=status_code, detail=detail)
        self.code = code or status_code


class NotFoundException(CustomException):
    """资源不存在异常"""
    def __init__(self, detail: str = "资源不存在"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            code=404
        )


class ValidationException(CustomException):
    """数据验证异常"""
    def __init__(self, detail: str = "数据验证失败"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            code=422
        )


class AuthenticationException(CustomException):
    """认证异常"""
    def __init__(self, detail: str = "认证失败"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            code=401
        )


class PermissionException(CustomException):
    """权限异常"""
    def __init__(self, detail: str = "权限不足"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            code=403
        )
