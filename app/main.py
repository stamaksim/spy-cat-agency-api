from fastapi import FastAPI

app = FastAPI(title="Spy Cat Agency API")


@app.get("/health")
def health():
    return {"status": "ok"}
