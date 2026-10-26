import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from starlette.exceptions import HTTPException as StarletteHTTPException

from api.schemas import ErrorResponse

logger = logging.getLogger("api")

ERROR_RESPONSES = {
    400: {"model": ErrorResponse, "description": "Dados da requisição inválidos"},
    404: {"model": ErrorResponse, "description": "Recurso não encontrado"},
    409: {"model": ErrorResponse, "description": "Conflito com o estado atual"},
    500: {"model": ErrorResponse, "description": "Erro interno do servidor"},
}


def _response(
    status_code: int,
    message: str,
    details: list[dict[str, str]] | None = None,
    headers: dict[str, str] | None = None,
):
    body = ErrorResponse(
        error={
            "code": status_code,
            "message": message,
            "details": details,
        }
    )
    return JSONResponse(
        status_code=status_code,
        content=body.model_dump(exclude_none=True),
        headers=headers,
    )


async def handle_http_exception(
    request: Request,
    exception: StarletteHTTPException,
):
    return _response(
        status_code=exception.status_code,
        message=str(exception.detail),
        headers=exception.headers,
    )


async def handle_validation_exception(
    request: Request,
    exception: RequestValidationError,
):
    details = [
        {
            "field": ".".join(str(part) for part in error["loc"]),
            "message": error["msg"],
        }
        for error in exception.errors()
    ]
    return _response(
        status_code=400,
        message="Dados da requisição inválidos",
        details=details,
    )


async def handle_integrity_exception(request: Request, exception: IntegrityError):
    logger.info("Operação rejeitada por restrição de integridade do banco")
    return _response(
        status_code=409,
        message="A operação viola uma regra de integridade dos dados",
    )


async def handle_unexpected_exception(request: Request, exception: Exception):
    logger.error(
        "Erro não tratado durante a requisição",
        exc_info=(type(exception), exception, exception.__traceback__),
    )
    return _response(
        status_code=500,
        message="Erro interno do servidor",
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(StarletteHTTPException, handle_http_exception)
    app.add_exception_handler(RequestValidationError, handle_validation_exception)
    app.add_exception_handler(IntegrityError, handle_integrity_exception)
    app.add_exception_handler(Exception, handle_unexpected_exception)
