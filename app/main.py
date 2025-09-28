from fastapi import FastAPI

app = FastAPI(title="Zehnly Duo API", version="1.0.0")


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}