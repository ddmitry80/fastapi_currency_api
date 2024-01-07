from typing import Any

from fastapi import HTTPException, status

print(f"module {__name__} import done")

class DetailedHTTPException(HTTPException):
    STATUS_CODE = status.HTTP_500_INTERNAL_SERVER_ERROR
    DETAIL = "Server error"

    def __init__(self, **kwargs: dict[str, Any]) -> None:
        super().__init__(status_code=self.STATUS_CODE, detail=self.DETAIL, **kwargs)


class PermissionDenied(DetailedHTTPException):
    STATUS_CODE = status.HTTP_403_FORBIDDEN
    DETAIL = "Permission denied"


class NotFound(DetailedHTTPException):
    STATUS_CODE = status.HTTP_404_NOT_FOUND


class BadRequest(DetailedHTTPException):
    STATUS_CODE = status.HTTP_400_BAD_REQUEST
    DETAIL = "Bad Request"


class NotAuthenticated(DetailedHTTPException):
    STATUS_CODE = status.HTTP_401_UNAUTHORIZED
    DETAIL = "User not authenticated"

    def __init__(self) -> None:
        super().__init__(headers={"WWW-Authenticate": "Bearer"})


class ExternalApiException(HTTPException):
    def __init__(self, detail: str = "Something went wrong on external service", status_code: int = 500):
        super().__init__(status_code=status_code, detail=detail)


class BadCurrencyCode(HTTPException):
    def __init__(self, detail: str = "Bad user request (maybe bad currency codes)", status_code: int = 400):
        super().__init__(status_code=status_code, detail=detail)


class CurrencyZeroRate(HTTPException):
    def __init__(self, detail: str = "One of currency rates is zero (division by zero)", status_code: int = 500):
        super().__init__(status_code=status_code, detail=detail)