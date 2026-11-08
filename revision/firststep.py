from fastapi import FastAPI , HTTPException, Path , Query
import json
app = FastAPI()
from revision.predefine import ModelName
from pydantic import BaseModel, EmailStr, ValidationError
from fastapi.middleware.cors import CORSMiddleware # CROSS ORIGN RESOURCE SHARING (CORS) is a security feature implemented by web browsers to restrict web pages from making requests to a different domain than the one that served the web page. It is a mechanism that allows servers to specify who can access their resources and how they can be accessed. CORS is implemented through HTTP headers that are sent by the server in response to a request made by a web page. The headers indicate whether the request is allowed or denied based on the origin of the request and the type of request being made.


app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"], # allow all origins
    allow_credentials = True, # allow all credentials
    allow_headers = ["*"], # allow all headers
    allow_methods = ["*"] # allow all methods
)


@app.get("/") # home page endpoint where on the URL the below message must be displayed
async def root():
    return {"message": "Hello World"}

@app.get("/hello") # hello page endpoint
def hello():
    return {"this is hello page"}

def load_data():
    with open("C:\\FastAPI\\student.json","r") as f:
        data = json.load(f)
    return data

@app.get("/student") # student page endpoint
def student():

    return load_data()


@app.get("/student/{id}") # student page endpoint with id
def student_by_id(id : str = Path(..., description="The ID of the student to retrieve")):
    data = load_data()
    for key , value in data.items():
        if key == id:
            return value
    raise HTTPException(status_code=404, 
        detail=f"Student id \"{id}\" not found")

@app.get("/model/{model_name}") # model page endpoint with model_name
def get_model(model_name : ModelName):
    if model_name == ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}

    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}

    return {"model_name": model_name, "message": "Have some residuals"}


@app.get("/filter_student") # filter student page endpoint with major
def filter_student(major: str = Query(None, description="The major of the student to filter by")):
    data = load_data()
    for key, value in data.items():
        if value["major"] == major:
            return {
                "id": key,
                "name": value["name"],
                "age": value["age"],
                "major": value["major"]
            }

"""
pagination 

"""

@app.get("/paginate")
def paginate_student(page:int = Query(1,ge=1 , description = "The page number to retrieve"),
                     limit: int = Query(10, ge=1, le=100, description="The number of students per page")):
    data = load_data()
    start_index = (page - 1) * limit
    end_index = start_index + limit
    Student_list = []
    for key , value in data.items():
        value["id"] = key 
        Student_list.append(value)
    student_list = Student_list[start_index:end_index]
    total_students = len(Student_list)
    return {
        "page": page,
        "limit": limit,
        "total_students": total_students,
        "students": student_list
    }

#halper function to save data to student.json
def save_data(data):
    with open("C:\\FastAPI\\student.json","w") as file :
        json.dump(data,file,indent=4)


"""Request Body
POST -> data comes in BODY (a JSON Object sent by the client)
when a function argument is pydantic model, FastAPI will automatically read the request body and convert it to a pydantic model instance
if it is not correct than it give BAD request error"""

from ppydantic.main import Student


@app.post("/create",status_code=201)
def create_student(student : Student):
    data = load_data()
    student_id = str(student.id)
    if student_id in data:
        raise HTTPException(status_code=400, 
        detail=f"Student id \"{student.id}\" already exists")
    data[student_id] = student.model_dump(exclude={"id","graded"})  # exclude is used to exclude the field from the model_dump() method
    save_data(data)
    return {"message": "Student created successfully", "student": student.model_dump()}


class updateStudent(BaseModel):
    name  : str | None = None
    age : int | None = None
    course : str | None = None
    email : EmailStr | None = None
    marks : int | None = None

@app.put("/update/{id}")
def update_student(student : updateStudent,
                   id : str = Path(..., description="The ID of the student to update")):
    data = load_data()
    student_id = str(id)
    if student_id not in data:
        raise HTTPException(
            status_code=404,
            detail=f'Student id "{student_id}" not found',
        )

    updates = student.model_dump(exclude_unset=True, exclude_none=True) # exclude_unset is used to exclude the fields that are not set in the request body and exclude_none is used to exclude the fields that are set to None in the request body
    data[student_id].update(updates)
    try:
        student_instance = Student(id=student_id, **data[student_id])
    except ValidationError as error:
        raise HTTPException(status_code=422, detail=error.errors()) from error

    data[student_id] = student_instance.model_dump(exclude={"id", "graded"})
    save_data(data)
    return {
        "message": "Student updated successfully",
        "student": student_instance.model_dump(),
    }

@app.delete("/delete/{id}")
def delete_student(id : str = Path(...,description = "the ID of the student to delete")):
    data = load_data()
    student_id = str(id)
    if student_id not in data:
        raise HTTPException(
            status_code = 404,
            detail = f"student_id \"{student_id}\" not found"
        )
    del data[student_id]
    save_data(data)
    return {"message": "Student deleted successfully"}
