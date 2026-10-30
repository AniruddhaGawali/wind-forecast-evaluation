import logging
import time
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import ALLOWED_ORIGINS, DEFAULT_CUTOFF, LOG_LEVEL
from app.logging_setup import configure_logging
from app.routes import analysis, health, raw, root
from app.services.analyzer import Analyzer
from app.services.data_store import load_data
from app.services.selection import parse_cutoff

logger = logging.getLogger("app")

DESCRIPTION = """
How good is the national GB wind forecast a day ahead?

Compares Elexon WINDFOR forecasts with FUELHH actual wind generation for delivery
2 Jan to 1 Feb 2026. For each target hour the API picks the latest forecast published
at or before a **cutoff** (UK time, on the day before delivery, default 09:00) and scores it
against the average of the two half-hour actuals in that hour.

* All timestamps are UTC. Dates (`start`, `end`) are UK delivery days, inclusive.
* `error = forecast - actual` (positive = over-forecast), in MW.
* Every error has the shape `{"detail": "..."}`.

Try `GET /api/v1/metrics?start=2026-01-02&end=2026-02-01&cutoff=09:00`.
"""


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    configure_logging(LOG_LEVEL)
    parse_cutoff(DEFAULT_CUTOFF)  # fail at start-up, not on the first request
    store = load_data()
    app.state.analyzer = Analyzer(store)
    logger.info(
        "data loaded",
        extra={
            "fields": {
                "actual_rows": len(store.actuals),
                "forecast_rows": len(store.forecasts),
            }
        },
    )
    yield


app = FastAPI(
    title="Wind Forecast Evaluation Portal",
    version="0.1.0",
    description=DESCRIPTION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    started = time.perf_counter()
    status = 500  # if call_next raises, the error handler answers with a 500
    try:
        response = await call_next(request)
        status = response.status_code
        return response
    finally:
        logger.info(
            "request",
            extra={
                "fields": {
                    "method": request.method,
                    "path": request.url.path,
                    "query": str(request.url.query),
                    "status": status,
                    "duration_ms": round((time.perf_counter() - started) * 1000, 1),
                }
            },
        )


@app.exception_handler(RequestValidationError)
async def validation_error(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Flatten FastAPI's list of errors into one readable sentence, like our own 422s."""
    parts = []
    for err in exc.errors():
        field = ".".join(
            str(p) for p in err["loc"] if p not in ("query", "path", "body")
        )
        parts.append(f"{field}: {err['msg']}" if field else err["msg"])
    return JSONResponse(status_code=422, content={"detail": "; ".join(parts)})


@app.exception_handler(Exception)
async def unexpected_error(request: Request, exc: Exception) -> JSONResponse:
    logger.error(
        "unhandled error",
        exc_info=exc,
        extra={"fields": {"method": request.method, "path": request.url.path}},
    )
    return JSONResponse(status_code=500, content={"detail": "Internal server error."})


app.include_router(root.router)
app.include_router(health.router)
app.include_router(raw.router)
app.include_router(analysis.router)


def main() -> None:
    import uvicorn

    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)


if __name__ == "__main__":
    main()
