from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None

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

@app.get("/items/{item_id}", response_model=Item)
def read_item(item_id : str):
    return items[item_id]


@app.put('/items/{item_id}', response_model=Item)
def update(item_id : str , item : Item):
    update_item_encoded = jsonable_encoder(item)
    items[item_id] = update_item_encoded
    return JSONResponse(content=update_item_encoded)

@app.patch('/items/{item_id}', response_model=Item)
def update_item(item_id : str , item : Item):
    sotred_item = items[item_id] # Retrieve the stored data.
    stored_model = Item(**sotred_item) # Create a Pydantic model instance from the stored data.
    update_data = item.model_dump(exclude_unset=True) # Get the data that was sent in the request, excluding any fields that were not set.
    updated_item = stored_model.model_copy(update=update_data) # Create a new Pydantic model instance by copying the stored model and updating it with the new data.
    items[item_id] = jsonable_encoder(updated_item)# Store the updated data in the items dictionary.
    return JSONResponse(content=jsonable_encoder(updated_item)) # Return the updated data as a JSON response.

