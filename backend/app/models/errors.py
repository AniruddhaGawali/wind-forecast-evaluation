from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """The shape of every error the API returns."""

    detail: str = Field(
        description="What went wrong, in plain English",
        examples=["start (2026-01-10) must be on or before end (2026-01-05)."],
    )


ERROR_RESPONSES: dict[int | str, dict[str, object]] = {
    422: {"model": ErrorResponse, "description": "Invalid query parameters"},
    500: {"model": ErrorResponse, "description": "Unexpected server error"},
}
