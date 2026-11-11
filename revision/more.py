from fastapi import FastAPI ,Body
from pydantic import BaseModel ,HttpUrl
from typing import Annotated, Set

app = FastAPI()

class Image(BaseModel):
    url: HttpUrl
    name: str

class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    tags : set[str] = set()  # default value is an empty set
    image : Image | None = None


@app.put("/items/{item_id}")
def update_item(item_id: int, item: Annotated[Item ,
                                              Body(openapi_examples={
                                                  "normal": {
                                                      "summary": "A normal example",
                                                    "description": "A **normal** item works correctly.",
                                                    "value": {
                                                        "name": "Foo",
                                                        "description": "A very nice Item",
                                                        "price": 35.4,
                                                        "tax": 3.2,
                                                    },
                                                                                                    },
                                                                                                    "invalid": {
                                                        "summary": "An invalid example",
                                                        "description": "An **invalid** item will cause an error.",
                                                        "value": {
                                                            "name": "Foo",
                                                            "description": "An invalid Item",
                                                            "price": 35.4,
                                                            "tax": 3.2,
                                                            "tags": ["invalid", 1],
                                                        },
                                                  },
                                              })]):
    

    results = {"item_id": item_id, "item": item}
    return results

