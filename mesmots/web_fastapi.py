import os
DEBUG = True if os.getenv("ENVIRON") else False
HOST = os.getenv("HOST", "0.0.0.0")
PORT = os.getenv("PORT", "8080")

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, ORJSONResponse
from pydantic import BaseModel
from simpleeval import SimpleEval
from mots import Mots

app = FastAPI()
mots = Mots("../dataset/")
seval = SimpleEval()

app.mount("/static/", StaticFiles(directory="static"), name="static")

seval.functions["startswith"] = lambda x: mots.startswith(x)
seval.functions["endswith"] = lambda x: mots.endswith(x)
seval.functions["contains"] = lambda x: mots.contains(x)
seval.functions["and"] = lambda x,y: mots.and_(x, y)
seval.functions["or"] = lambda x,y: mots.or_(x, y)
seval.functions["xor"] = lambda x,y: mots.xor_(x, y)

@app.get("/")
async def index():
    return RedirectResponse("/static/index.html", status_code=301)

@app.get("/api/v1/split/{word}/", response_class=ORJSONResponse)
async def split(word: str):
    res = await mots.split(word)
    if len(res) == 0:
        raise HTTPException(status_code=400, detail="The word provided is not found in the database")
    return {"splits": res}

class INFindSchema(BaseModel):
    text: str

@app.post("/api/v1/find/", response_class=ORJSONResponse)
async def find(body: INFindSchema):
    try:
        res = seval.eval(body.text)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to compute: {e}")
    words = await mots.apply(res)
    return {"words": words}

def start():
    uvicorn.run("web_fastapi:app", host=HOST, port=int(PORT))