from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["meta"])


class Health(BaseModel):
    status: str


@router.get("/health", response_model=Health, summary="Liveness check")
def health() -> Health:
    """Returns `{"status": "ok"}` once the data is loaded and the API is serving."""
    return Health(status="ok")
