from fastapi import FastAPI 
from models import product
app = FastAPI()
@app.get("/")
def greet():
    return "welcome to telusko trac"

products = [
    product(id=1, name="phone", description="budget phone", price=100, quantity=1),
    product(id=2, name="laptop", description="budget laptop", price=1000, quantity=1),
    product(id=3, name="console", description="budget console", price=10000, quantity=1),
]

@app.get("/products")
def get_all_products():
    return products

@app.get("/product/{id}")
def get_product_by_id(id:int):
    for p in products:
        if p.id == id:
            return p
    return {"error": "Product not found"}

@app.post("/product")
def create_product(product:product):
    products.append(product)
    return product


@app.put("/product/{id}")
def update_product(id: int, updated_product: product):
    for i, existing_product in enumerate(products):
        if existing_product.id == id:
            products[i] = updated_product
            return {"message": "product updated successfully", "product": products[i]}
    return {"message": "no product found"}


@app.delete("/product")
def delete_product(id: int ):
    for i in range(len(products)):
        if products[i].id == id:
            del products[i]
            return f" its delelted id {id}"
    return f"no that id"