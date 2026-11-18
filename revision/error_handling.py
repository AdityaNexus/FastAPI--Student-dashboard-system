from fastapi import FastAPI , HTTPException , Request
from fastapi.responses import JSONResponse
from fastapi.exception_handlers import (
    http_exception_handler,
    request_validation_exception_handler,
)
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as Star
from fastapi.encoders import jsonable_encoder


app = FastAPI()

items = {
    "id1" : "hero",
    "id2" : "ero2",
}

@app.get("/item/{item_id}")
def read_item(item_id : str ):
    if item_id not in items:
        raise Star(
            status_code = 404 ,
            detail = "Item is not in inventory",
            headers = {"X-Error" : "There is an error"}
        )
    return {"item" : items[item_id]}

class UnicornException(Exception):
    def __init__(self, name: str):
        self.name = name


@app.exception_handler(UnicornException)
def unicorn_exception_handler(request : Request, exc: UnicornException):
    return JSONResponse(
        status_code=418,
        content={"message": f"Oops! {exc.name} did something. There goes a rainbow...",
                 "failed_url": str(request.url)},
    )


@app.get("/unicorns/{name}",tags = ["GET"],summary="dont type yolo gives error")
def read_uvicorn(name : str):
    """
    give the name of uvicorn
    but dont type yolo
    """
    if name  == "lola":
        raise UnicornException(name = name)
    return {"uvicorn_name" : name}


@app.exception_handler(Star)
async def custom_http_exception_handler(request, exc):
    # 1. Do your custom logging first
    print(f"LOG ALERT: HTTP error {exc.status_code} at {request.url}: {exc.detail}")
    
    # 2. Let FastAPI return its normal default JSON error response
    return await http_exception_handler(request, exc)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    # 1. Log the bad payload sent by the client
    print(f"LOG ALERT: Validation failed for body: {exc.body}")
    
    # 2. Let FastAPI return its normal default 422 JSON response
    return await request_validation_exception_handler(request, exc)


from pydantic import BaseModel
from datetime import datetime
from pathlib import Path

try:
    from .fakeDb import fake_db, save_fake_db,get_txt_file,txt_halper
except ImportError:
    from fakeDb import fake_db, save_fake_db, get_txt_file, txt_halper

class Item(BaseModel):
    title : str 
    timestamp : datetime
    description : str | None = None


@app.put("/item/{id}",summary="fill the facke_db",response_description="store data in db")
def update_item(id : str , item : Item):
    if id in fake_db:
        raise HTTPException(
            status_code=400,
            detail=f"Item with ID '{id}' already exists in the fake database.",
        )

    json_compatible = jsonable_encoder(item)
    fake_db[id] = json_compatible
    save_fake_db(fake_db)

    return {"message": "Item updated successfully"}


@app.get("/fake-db")
def get_fake_db():
    return fake_db



@app.put("/data",summary="store data in txt file",response_description="store data in txt file")
def update_txt(data : str,path : str|None = None):
    if data is None:
        raise HTTPException(
            status_code=404 , detail = "not data"
        )
    return txt_halper(data, path)


    