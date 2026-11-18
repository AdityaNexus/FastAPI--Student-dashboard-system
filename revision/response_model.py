from pydantic import BaseModel , EmailStr
from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from typing import Any
app = FastAPI()

class UserIn(BaseModel):
    name: str 
    id : int 
    password : int 


class UserOut(BaseModel):
    name : str 
    id : int 
    status : str | None = "Success"

@app.post("/user",response_model=UserOut)
def work(user: UserIn) -> Any:
    return user

class BaseUser(BaseModel):
    username: str
    email: EmailStr
    full_name: str | None = None


class UserIn1(BaseUser):
    password: str


@app.post("/user1")
def create_user(user: UserIn1) -> BaseUser:
    return user


@app.get("/portal", response_model=None)
async def get_portal(teleport: bool = False) -> Response | dict:
    if teleport:
        return RedirectResponse(url="/video-page")
    return {"message": "Here's your interdimensional portal."}


@app.get("/video-page", response_class=HTMLResponse)
async def video_page() -> HTMLResponse:
    video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    return HTMLResponse(
        content=f"""
        <html>
            <body>
                <h1>Video page</h1>
                <p>
                    <a href="{video_url}" target="_blank">
                        Open the YouTube video
                    </a>
                </p>
            </body>
        </html>
        """
    )





class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float = 10.5


items = {
    "foo": {"name": "Foo", "price": 50.2},
    "bar": {"name": "Bar", "description": "The Bar fighters", "price": 62, "tax": 20.2},
    "baz": {
        "name": "Baz",
        "description": "There goes my baz",
        "price": 50.2,
        "tax": 10.5,
    },
}


@app.get(
    "/items/{item_id}/name",
    response_model=Item,
    response_model_include={"name", "description"},
)
async def read_item_name(item_id: str):
    return items[item_id]


@app.get("/items/{item_id}/public", response_model=Item, response_model_exclude={"tax"})
async def read_item_public_data(item_id: str):
    return items[item_id]
"""
You can also use:

response_model_exclude_defaults=True
response_model_exclude_none=True
"""


