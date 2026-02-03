import os
DEBUG = True if os.getenv("ENVIRON") else False
HOST = os.getenv("HOST", "0.0.0.0")
PORT = os.getenv("PORT", "8080")

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

from api import subapi

app = FastAPI()

@app.get("/")
def index():
    return RedirectResponse("/static/index.html", status_code=301)

app.mount("/static/", StaticFiles(directory="static"), name="static")
app.mount("/api", subapi)

def start():
    uvicorn.run("main:app", host=HOST, port=int(PORT))
