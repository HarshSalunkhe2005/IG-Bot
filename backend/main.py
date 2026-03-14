import uvicorn
from fastapi import FastAPI
# Note the change in import style because we are already inside 'backend'
from api.routes import router as api_router

app = FastAPI(title="IG-Bot API")

app.include_router(api_router, prefix="/api")

@app.get("/")
def read_root():
    return {"status": "IG-Bot Backend is Online"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)