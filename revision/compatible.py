import json
from datetime import datetime
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

class Order(BaseModel):
    item :str 
    order_date : datetime

order = Order(item="Laptop", order_date=datetime.now())

python_dict = order.model_dump()
json_dict = order.model_dump(mode="json")
fastapi_dict = jsonable_encoder(order)
json_text = order.model_dump_json(indent=4)
parsed_dict = json.loads(json_text)
restored_model = Order.model_validate(parsed_dict)

print(python_dict["order_date"], type(python_dict["order_date"]))
print(json_dict["order_date"], type(json_dict["order_date"]))
print(fastapi_dict["order_date"], type(fastapi_dict["order_date"]))
print(json_text, type(json_text))
print(parsed_dict, type(parsed_dict))
print(restored_model, type(restored_model))