from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def root_status():
    return {"status": "ok"}
