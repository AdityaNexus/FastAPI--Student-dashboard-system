from pydantic import BaseModel


class product(BaseModel):
    id : int
    name : str
    description : str
    price : int 
    quantity : int
