import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.middleware.request_context import RequestContextMiddleware
from app.api.routes import employees, insights
from app.core.config import get_settings
from app.core.exceptions import DomainError
from app.core.logging import configure_logging
from app.db.session import engine, init_db

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    configure_logging(settings.log_level)
    init_db(engine)
    yield


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(DomainError)
    async def _domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
        logger.warning(
            "domain_error",
            extra={
                "code": exc.code,
                "status_code": exc.status_code,
                "method": request.method,
                "path": request.url.path,
            },
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message, "code": exc.code},
        )

    @app.exception_handler(Exception)
    async def _unhandled_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        logger.exception(
            "unhandled_exception",
            extra={
                "exception_type": type(exc).__name__,
                "method": request.method,
                "path": request.url.path,
            },
        )
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error", "code": "internal_error"},
        )


app = FastAPI(title="Salary Management API", lifespan=lifespan)
# RequestContextMiddleware is added BEFORE CORSMiddleware so that CORS
# remains the outermost middleware in the Starlette stack (last added is
# outermost), which lets it short-circuit OPTIONS preflights cleanly.
app.add_middleware(RequestContextMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Total-Count", "X-Request-ID"],
)
register_exception_handlers(app)

app.include_router(employees.router)
app.include_router(insights.router)


@app.get("/")
def root() -> dict[str, str]:
    return {"status": "ok"}
