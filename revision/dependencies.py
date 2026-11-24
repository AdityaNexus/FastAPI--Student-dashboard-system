from typing import Annotated
from unicodedata import name
from fastapi import Depends, FastAPI ,  Header , HTTPException

app = FastAPI()

def common_parameters(q: str | None = None, skip: int = 0, limit: int = 100):
    return {"q": q, "skip": skip, "limit": limit}

@app.get("/items/")
def read_items(commons: Annotated[dict, Depends(common_parameters)]):
    return commons

@app.get("/users/")
def read_users(commons: Annotated[dict, Depends(common_parameters)]):
    return commons

FAKE_USERS_DB = {
    "token_aman": {"username": "Aman", "active": True, "is_admin": False, "is_pro": False},
    "token_priya": {"username": "Priya", "active": True, "is_admin": False, "is_pro": True},
    "token_boss": {"username": "Vikram", "active": True, "is_admin": True, "is_pro": True},
    "token_banned": {"username": "Rohit", "active": False, "is_admin": False, "is_pro": True},
}

# ==========================================
# LEVEL 1: Base Dependency (Who is the user?)
# ==========================================
def get_current_user(token : str):
    user = FAKE_USERS_DB.get(token)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid authentication credentials")
    return user

# ==========================================
# LEVEL 2: Sub-Dependencies (Depends on Level 1)
# ==========================================
def get_active_user(
        current_user : Annotated[dict , Depends(get_current_user)]
):
    if not current_user["active"]:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user



def get_admin_user(
        current_user : Annotated[dict , Depends(get_current_user)]
):
    if not current_user["is_admin"]:
        raise HTTPException(status_code=400, detail="User is not an admin")
    return current_user


# ==========================================
# LEVEL 3: Sub-Sub-Dependency (Depends on Level 2)
# ==========================================
async def get_paying_user(
    active_user: Annotated[dict, Depends(get_active_user)]
):
    if not active_user["is_pro"]:
        raise HTTPException(status_code=402, detail="Pro subscription required")
    return active_user

# ==========================================
# ENDPOINTS: Plug in ONLY the final level needed
# ==========================================


# 1. Public : NO Dependecies at all
@app.get("/items/public/")
def read_public_items():
    return {"items": ["public_item1", "public_item2"]}


# 2. Private : Depends on Level 1
@app.get("/items/private/")
def read_private_items(
    user : Annotated[dict , Depends(get_current_user)]
):
    return {"Messages" : f"welcone {user['username']} to private items"}



# 3. Pro: Triggers get_current_user -> get_active_user -> get_paying_user
@app.get("/items/pro/")
async def read_pro_items(
    user: Annotated[dict, Depends(get_paying_user)]
):
    return {"message": f"Pro access for {user['username']}", "items": ["AI Source Code"]}


# 4. Admin: Triggers get_current_user -> get_admin_user
@app.post("/users/{user_id}/activate")
async def activate_user(
    user_id: str,
    admin: Annotated[dict, Depends(get_admin_user)],
):
    return {"status": f"User {user_id} activated by Admin {admin['username']}"}


# Using class-based dependencies

fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]


class CommonQueryParams:
    def __init__(self, q: str | None = None, skip: int = 0, limit: int = 100):
        self.q = q
        self.skip = skip
        self.limit = limit


@app.get("/items/class/")
def read_items(commons: Annotated[CommonQueryParams, Depends(CommonQueryParams)]):
    response = {}
    if commons.q:
         response.update({"q": commons.q})
    fake = {commons.skip : commons.skip + commons.limit}
    items = fake_items_db[commons.skip : commons.skip + commons.limit]


    response.update({"items": items})
    response.update({"fake": fake})
    return response


def verify_token(x_token: Annotated[str, Header()]):
    if x_token != "fake-super-secret-token":
        raise HTTPException(status_code=400, detail="X-Token header invalid")

def verify_key(x_key : Annotated[str , Header()]):
    if x_key != "fake-super-secret-key":
        raise HTTPException(status_code=400, detail="X-Key header invalid")

#app = FastAPI(dependencies=[Depends(verify_token), Depends(verify_key)]) this will apply the dependencies to all endpoints in the app
# no need to add the dependencies to each endpoint individually.

@app.get("/items/headers/",dependencies =[Depends(verify_token), Depends(verify_key)])
def read_items():
    return [{"item": "Foo"}, {"item": "Bar"}]


class FakeSession:
    def __init__(self):
        self.is_open = True
        print("FakeSession: Opened a new session")

    def query_user(self , user_id : int):
        if user_id !=1:
            raise HTTPException(status_code=404, detail="User not found")
        return {"user_id" : 1 , "name" : "Aman" }

    def close(self):
        self.is_open = False
        print("FakeSession: Closed the session")


# THE DEPENDENCY WITH `yield` (Notice: do NOT add @contextmanager here; FastAPI does it internally)
async def get_db():
    db = FakeSession()
    try:
        yield db  # <-- Pauses here and injects `db` into your endpoint!
    finally:
        # <-- Always runs AFTER the endpoint finishes (even if an HTTPException occurred!)
        db.close()



@app.get("/users/DB/{user_id}")
async def read_user(
    user_id: int,
    db: Annotated[FakeSession, Depends(get_db)],
):
    print("2. [ENDPOINT] Running query inside endpoint...")
    return db.query_user(user_id)

