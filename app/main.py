from fastapi import FastAPI

app = FastAPI(title="Salary Management API")


@app.get("/")
def root() -> dict[str, str]:
    return {"status": "ok"}
