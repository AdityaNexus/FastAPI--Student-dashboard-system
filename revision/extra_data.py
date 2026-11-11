from datetime import datetime, time, timedelta
from uuid import UUID
from typing import Annotated
from fastapi import Body, FastAPI,Header , HTTPException
from pydantic import BaseModel , EmailStr
app = FastAPI()


@app.put("/items/{item_id}")
async def read_items(
    item_id: UUID,
    start_datetime: datetime = Body(),
    end_datetime: datetime = Body(),
    process_after: timedelta = Body(),
    repeat_at: time | None = Body(default=None),
):
    start_process = start_datetime + process_after
    duration = end_datetime - start_process
    return {
        "item_id": item_id,
        "start_datetime": start_datetime,
        "end_datetime": end_datetime,
        "process_after": process_after,
        "repeat_at": repeat_at,
        "start_process": start_process,
        "duration": duration,
    }



@app.get("/secure-data/")
def get_secure_data(
    x_api_key : Annotated[str|None , Header(description="API Key for authentication")] = None,
    user_id : Annotated[str|None, Header(description="User ID")] = None
):
    if x_api_key != "my-secret-office-key-123":
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return {
        "status": "success",
        "message": "You have access to secure data.",
        "client_user_id": user_id,
    }

class BaseUser(BaseModel):
    username : str 
    email : EmailStr
    full_name : str | None = None

class UserIn(BaseUser):
    password : str


@app.post("/user/")
def create_user(user : UserIn)-> BaseUser:
    return user