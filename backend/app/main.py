from fastapi import FastAPI

from app.routes import health, root

app = FastAPI(title="Wind Forecast Evaluation Portal", version="0.1.0")

app.include_router(root.router)
app.include_router(health.router)


def main() -> None:
    import uvicorn

    uvicorn.run("app.main", host="127.0.0.1", port=8000, reload=True)


if __name__ == "__main__":
    main()
