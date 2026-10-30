from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["meta"])


class Index(BaseModel):
    name: str
    docs: str


@router.get("/", response_model=Index, summary="API index")
def index() -> Index:
    """Name of the API and where to find the interactive docs."""
    return Index(name="Wind Forecast Evaluation Portal API", docs="/docs")
