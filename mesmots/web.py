from bottle import Bottle, debug, abort, view, request
from simpleeval import SimpleEval
debug(True)

from mots import Mots

app = Bottle()
mots = Mots("../Lexique383/Lexique383.tsv")
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
    return {}

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
    text = request.json["text"]
    res = seval.eval(text)
    words = mots.apply(res)
    return {"words": words}


def start():
    app.run(host="0.0.0.0", port=8080, debug=True, reloader=True)
