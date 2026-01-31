import os
DEBUG = True if os.getenv("ENVIRON") else False
HOST = os.getenv("HOST", "0.0.0.0")
PORT = os.getenv("PORT", "8080")
from bottle import debug
debug(DEBUG)

from bottle import Bottle, abort, view, request
from simpleeval import SimpleEval

from mots import Mots

app = Bottle()
mots = Mots("../Lexique383/Lexique383.csv")
seval = SimpleEval()

seval.functions["startswith"] = lambda x: mots.startswith(x)
seval.functions["endswith"] = lambda x: mots.endswith(x)
seval.functions["contains"] = lambda x: mots.contains(x)
seval.functions["and"] = lambda x,y: mots.and_(x, y)
seval.functions["or"] = lambda x,y: mots.or_(x, y)
seval.functions["xor"] = lambda x,y: mots.xor_(x, y)

@app.route("/")
@view("index.html")
def index():
    return {"DEBUG": "true" if DEBUG else "false"}

@app.route("/api/v1/split/<word>/")
def split(word: str):
    res = mots.split(word)
    if len(res) == 0:
        abort(400, "The word provided is not found in the database")
    return {"splits": res}

@app.route("/api/v1/find/", "POST")
def find():
    if request.content_type != "application/json":
        abort(400, "The content_type must be 'application/json'")
    if "text" not in request.json:
        abort(400, "The 'text' is not in json body")
    text = request.json["text"]
    try:
        res = seval.eval(text)
    except Exception as e:
        abort(400, f"Failed to compute: {e}")
    words = mots.apply(res)
    return {"words": words}


def start():
    app.run(host=HOST, port=int(PORT), debug=DEBUG, reloader=DEBUG)
