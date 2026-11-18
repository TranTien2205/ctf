# Python NoSQL — the pymongo/flask/django carriers

## `pymongo` — the driver

```python
from pymongo import MongoClient
client = MongoClient()
db = client.db
db.users.find_one({"user": {"$ne": None}})
db.users.find({"user": {"$ne": None}})
db.users.find_one({"user": request.json["user"], "pass": request.json["pass"]})
db.users.find_one({"user": request.form["user"], "pass": request.form["pass"]})
db.users.find_one({"user": request.args.get("user"), "pass": request.args.get("pass")})
db.users.find_one({"user": request.cookies.get("user")})
db.users.find_one({"user": request.headers.get("x-user")})
db.users.find_one(request.json)
db.users.find(request.json)
db.users.find_one(request.get_json())
db.users.find_one(json.loads(request.data))
db.users.find_one(json.loads(request.args.get("q")))
db.users.find_one(json.loads(request.headers.get("x-filter")))
db.users.find_one(dict(request.args))
db.users.find_one(dict(request.form))
db.users.find_one(dict(request.cookies))
db.users.find_one(dict(request.headers))
db.users.find_one(dict(request.json))
db.users.find_one(dict(request.form))
db.users.find_one(dict(request.args))
```

`pymongo` — the `find_one`/`find`/`count_documents`/`distinct`/
`aggregate`/`update_one`/`update_many`/`replace_one`/`delete_one`/
`delete_many`/`insert_one`/`insert_many`/`bulk_write` — the dict-body
reaches the filter — `injection-points.md`.

## `flask` — the `request.json` carrier

```python
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()           — {"user": {"$ne": null}}
    user = db.users.find_one({"user": data["user"], "pass": data["pass"]})
    if user:
        return jsonify({"token": sign(user)})
    return jsonify({"error": "invalid"}), 401
```

`request.get_json()` — the JSON-body — `{"user": {"$ne": null}}` —
`injection-points.md`.

## `flask` — the `request.form` carrier

```python
@app.route("/login", methods=["POST"])
def login():
    user = db.users.find_one({
        "user": request.form["user"],   — "user[$ne]=x" stays a string
        "pass": request.form["pass"]
    })
```

`request.form` — the form-data — `user[$ne]=x` stays a literal STRING —
the flat-carrier — `denied-conditions.md` — python's `request.form` is
NOT qs — the `[$ne]` is a literal key.

## `flask` — the `request.args` carrier

```python
@app.route("/search")
def search():
    users = list(db.users.find(dict(request.args)))
```

`dict(request.args)` — `?user[$ne]=x` → `{"user[$ne]": "x"}` — the flat-
dict — `denied-conditions.md` — the `[$ne]` is a literal key, not nested.

## `django` — the `request.POST`/`request.GET`

```python
from django.http import JsonResponse

def login(request):
    data = json.loads(request.body)
    user = db.users.find_one({"user": data["user"], "pass": data["pass"]})
```

`request.POST`/`request.GET`/`request.body` — the flat-parser —
`injection-points.md`.

## `django` — the `QueryDict` — the `getlist`

```python
def search(request):
    q = request.GET.get("q")
    users = list(db.users.find({"user": {"$regex": q}}))
```

`request.GET.get` — the query-param — `injection-points.md`.

## `python` — the `json.loads` — the string-carrier

```python
data = json.loads(request.body)
q = json.loads(request.args.get("q"))
filter = json.loads(request.headers.get("x-filter"))
```

`json.loads` — the string-JSON — `carrier-json-deep.md`.

## `python` — the `dict`/`literal_eval` — the object-carrier

```python
import ast
filter = ast.literal_eval(request.args.get("q"))
```

`ast.literal_eval` — the python-dict-literal — `{"$ne": null}` as a
python-dict — `injection-points.md` — the `literal_eval` parses
python-syntax, not JSON — `True`/`None` vs `true`/`null`.

## `python` — the `bson` — the BSON-carrier

```python
from bson import json_util, ObjectId
data = json_util.loads(request.body)      — EJSON
data = json_util.loads(request.data)      — EJSON
db.users.find_one({"_id": ObjectId(request.args.get("id"))})
```

`bson.json_util` — the EJSON — `{"$oid": "..."}`/`{"$date": "..."}` —
`carrier-json-deep.md`.

## `python` — the `mongoengine` — the ODM

```python
from mongoengine import connect
class User(Document):
    user = StringField()
    pass_ = StringField()

User.objects(user=request.json["user"], pass_=request.json["pass"])
User.objects(user__ne=None, pass___ne=None)
User.objects(user__regex="^a", pass___regex="^a")
User.objects(user__icontains="admin")
User.objects(__raw__={"user": {"$ne": None}})
User.objects(__raw__=request.json)
User.objects(__raw__=json.loads(request.body))
```

`mongoengine` — the `__raw__` — the object-carrier — `injection-points.md`.

## `python` — the `motor` — the async-driver

```python
from motor.motor_asyncio import AsyncIOMotorClient
client = AsyncIOMotorClient()
await client.db.users.find_one({"user": {"$ne": None}})
await client.db.users.find_one(request.json)
```

`motor` — the async-pymongo — `injection-points.md`.

## `python` — the `beanie` — the async-ODM

```python
from beanie import Document
class User(Document):
    user: str
    pass_: str

await User.find_one({"user": {"$ne": None}})
await User.find_one(request.json)
await User.find({"user": {"$ne": None}}).to_list()
```

`beanie` — the pydantic-ODM — `injection-points.md`.

## `python` — the `flask-pymongo` — the wrapper

```python
from flask_pymongo import PyMongo
mongo = PyMongo(app)
mongo.db.users.find_one({"user": request.json["user"]})
mongo.db.users.find_one(request.json)
```

`flask-pymongo` — `injection-points.md`.

## `python` — the `fastapi` — the pydantic

```python
from fastapi import FastAPI, Body
from pydantic import BaseModel

class Login(BaseModel):
    user: str
    pass_: str

@app.post("/login")
def login(data: Login):
    user = db.users.find_one({"user": data.user, "pass": data.pass_})
```

`pydantic`'s `BaseModel` — the `str`/`int`/`ObjectId`/`Any`/`dict`/
`Json`/`JsonValue`/`RawJson`/`SecretStr`/`SecretBytes`/`StrictStr`/
`StrictInt`/`StrictBool`/`ConstrainedStr`/`EmailStr`/`HttpUrl`/
`IPvAnyAddress`/`PaymentCardNumber`/`ByteSize`/`DirectoryPath`/
`FilePath`/`Json`/`UUID` — the `str`-typed field rejects an object —
`denied-conditions.md` — but `dict`/`Json`/`Any`-typed accepts —
`filter-bypass.md`.

## `python` — the `eval`/`exec` — the JS-eval

```python
eval(request.args.get("q"))
exec(request.args.get("q"))
```

`eval`/`exec` — the python-eval — different class —
`misc-interpreter-escape`.
