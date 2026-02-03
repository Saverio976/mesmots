from fastapi import FastAPI, HTTPException
from fastapi.responses import ORJSONResponse
from pydantic import BaseModel
import polars as pl
from mots import Mots

mots = Mots("../dataset/")
subapi = FastAPI()

@subapi.get("/v1/split/{word}/", response_class=ORJSONResponse)
async def split(word: str):
    res = await mots.split(word)
    if len(res) == 0:
        raise HTTPException(status_code=400, detail="The word provided is not found in the database")
    return {"splits": res}

class INFindSchema(BaseModel):
    text: str

@subapi.post("/v1/find/", response_class=ORJSONResponse)
async def find(body: INFindSchema):
    try:
        res = mots.seval.eval(body.text)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to compute: {e}")
    if not isinstance(res, pl.Expr):
        raise HTTPException(status_code=400, detail="You need to use the functions provided")
    words = await mots.apply(res)
    return {"words": words}

@subapi.get("/v1/plot/{syllab}/", response_class=ORJSONResponse)
async def plot(syllab: str):
    res = await mots.plot(syllab)
    return {"before": res[0], "after": res[1]}
