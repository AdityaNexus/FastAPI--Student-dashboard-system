import os
import time
from pathlib import Path as FilePath

from pydantic import BaseModel ,EmailStr, Field ,field_validator ,computed_field ,ConfigDict
from fastapi import FastAPI , HTTPException, Path , Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker , DeclarativeBase,Session
from sqlalchemy.exc import IntegrityError, OperationalError

load_dotenv()
from sqlalchemy import create_engine , text ,Column ,String , Integer,func
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL must be set")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

sessionlocal = sessionmaker(bind=engine)

class base(DeclarativeBase):
    pass

class StudentDB(base):
    __tablename__ = "student_records"
    id      = Column(String, primary_key=True)
    name    = Column(String(50), nullable=False)
    age     = Column(Integer, nullable=False)
    course  = Column(String(50), nullable=False)
    email   = Column(String, unique=True, nullable=False)  
    marks   = Column(Integer, nullable=False)


# Part 5 : Pydantic schemas for input (StudentCreate , StudentUpdate)
class StudentCreate(BaseModel):
    id : str = Field(...,examples={"001"})
    name : str = Field(...,min_length=1,max_length=50,examples={"aditya"})
    age : int = Field(...,ge=0,le=150,examples={20})
    course : str = Field(...,min_length=1,max_length=50,examples={"Btech"})
    email : EmailStr
    marks : int = Field(...,ge=0,le=100,examples={100})
    @field_validator("name")
    @classmethod
    def check_name(cls , value):
        if value.replace(" ","").isalpha() == False:
            raise ValueError("Name must contain only alphabets and spaces")
        return value.title()  # Capitalize the first letter of each word


class StudentUpdate(BaseModel):
    name : str = Field(None,min_length=1,max_length=50,examples={"aditya"})
    age : int = Field(None,ge=0,le=150,examples={20})
    course : str = Field(None,min_length=1,max_length=50,examples={"Btech"})
    email : EmailStr = None
    marks : int = Field(None,ge=0,le=100,examples={100})

    @field_validator("name")
    @classmethod
    def check_name(cls , value):
        if value.replace(" ","").isalpha() == False:
            raise ValueError("Name must contain only alphabets and spaces")
        return value.title()  # Capitalize the first letter of each word

#part 6 : Pydantic schema for output(StudentResponse , StudentPage , Message)
class StudentResponse(StudentCreate):
    model_config = ConfigDict(from_attributes=True)  # from_attributes=True means that the model will be created from the attributes of the object
    @computed_field
    @property
    def grade(self)->str:
        if self.marks >= 90:
            return "A"
        elif self.marks >= 80:
            return "B"
        elif self.marks >= 70:
            return "C"
        elif self.marks >= 60:
            return "D"
        else:
            return "F"

# part 7 : get_db() - one session per request
# Opens a session , gives it to the endpoint , always closes it , replace load_data/ save_data 
def get_db():
    db = sessionlocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def initialize_database():
    for attempt in range(30):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            base.metadata.create_all(engine)
            return
        except OperationalError:
            if attempt == 29:
                raise
            time.sleep(2)

# Part 9: GET one student
#Depends(get_db()) - before the endpoint is called , get_db() is called and the session is passed to the endpoint
@app.get("/students/{student_id}", response_model=StudentResponse,tags=["GET ROUTE"])
def get_student(student_id : str = Path(...,description = "The Id of the student to get"),
                                        db : Session = Depends(get_db)):
    student = db.get(StudentDB , student_id) # SELECT * FROM student_records WHERE id = student_id in query
    if student is None:
        raise HTTPException(status_code=404 , detail=f"Student with id {student_id} not found")
    return student


@app.get("/student/{student_id}", response_model=StudentResponse, include_in_schema=False)
def get_student_legacy(student_id: str, db: Session = Depends(get_db)):
    return get_student(student_id, db)

# Part 10: POST - create a student

@app.post("/CreateStudent",response_model=StudentResponse,status_code=201,tags=["POST ROUTE"])
def create_student(student : StudentCreate ,
                   db : Session = Depends(get_db)):
    if db.get(StudentDB , student.id):
        raise HTTPException(status_code=400 , detail=f"Student with id {student.id} already exists")
    new_student = StudentDB(**student.model_dump())  # unpack the student model into the StudentDB model
    db.add(new_student)
    try:
        db.commit()
        db.refresh(new_student)  # refresh the new_student object with the data from the database
    except IntegrityError as e:
        db.rollback()  # rollback the transaction if there is an integrity error
        raise HTTPException(status_code=400 , detail=f"Integrity error: {str(e)}")
    return new_student


@app.post("/create", response_model=StudentResponse, status_code=201, include_in_schema=False)
def create_student_legacy(student: StudentCreate, db: Session = Depends(get_db)):
    return create_student(student, db)


# Part 11: PUT - Update a student
@app.put("/updateStudent/{student_id}",tags=["PUT ROUTE"])
def update_student(student : StudentUpdate,
                   student_id : str = Path(...,description = "The Id of the student to update"),
                   db : Session = Depends(get_db)):
    student_in_db = db.get(StudentDB , student_id)
    if student_in_db is None:
        raise HTTPException(status_code=404 , detail=f"Student with id {student_id} not found")
    changes = student.model_dump(exclude_unset = True , exclude_none = True)  # exclude_unset = True means that only the fields that are set in the request body will be included in the changes dictionary and exclude_none = True means that only the fields that are not None will be included in the changes dictionary
    for key , value in changes.items():
        setattr(student_in_db , key , value)  # setattr(object , attribute , value) is used to set the value of an attribute of an object
    try:
        db.commit()
        db.refresh(student_in_db)
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400 , detail=f"Integrity error: {str(e)}")
    return student_in_db


@app.put("/update/{student_id}", response_model=StudentResponse, include_in_schema=False)
def update_student_legacy(
    student: StudentUpdate, student_id: str, db: Session = Depends(get_db)
):
    return update_student(student, student_id, db)


# 12 - DELETE - Delete a student

@app.delete("/deleteStudent/{student_id}",tags=["DELETE ROUTE"])
def delelte_student(student_id : str = Path(...,description = "The Id of the student to delete"),
                    db : Session = Depends(get_db)):
    student_in_db = db.get(StudentDB , student_id)
    if student_in_db is None:
        raise HTTPException(status_code=404 , detail=f"Student with id {student_id} not found")

    student_name = student_in_db.name
    db.delete(student_in_db)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400 , detail=f"Integrity error: {str(e)}")
    return f"Student with id {student_id} and name {student_name} deleted successfully"


@app.delete("/delete/{student_id}", include_in_schema=False)
def delete_student_legacy(student_id: str, db: Session = Depends(get_db)):
    return delelte_student(student_id, db)



# Part 13 -> GET all students (filter + sort + paginate)

SORT_FIELDS = ["marks","age","name"]
SORT_ORDERS = ["asc","desc"]

@app.get("/students",tags=["GET ROUTE"])
def get_all(
    course : str|None = Query(None , description = "show only students on their course"),
    sort_by : str | None = Query(None, description = f"sort by field , available fields are {SORT_FIELDS}"),
    order : str   = Query("asc", description = f"sort order , available orders are {SORT_ORDERS}"),
    page : int = Query(1, ge=1, description="page number"),
    limit : int = Query(10, ge=1, le=100, description="number of students per page"),
    db : Session = Depends(get_db)
):
    if sort_by is not None and sort_by not in SORT_FIELDS:
        raise HTTPException(status_code=400 , detail=f"Invalid sort field {sort_by} , available fields are {SORT_FIELDS}")

    if order is not None and order not in SORT_ORDERS:
        raise HTTPException(status_code=400 , detail=f"Invalid sort order {order} , available orders are {SORT_ORDERS}")

    query = db.query(StudentDB) # SELECT * FROM student_records
    if course:
        query = query.filter(func.lower(StudentDB.course) == course.lower())  # filter by course , case insensitive
    
    # get the total number of students after filtering
    total_students = query.count()  # get the total number of students after filtering

    if sort_by:
        column = getattr(StudentDB , sort_by)  # get the column object from the StudentDB class
        if order == "desc":
            query = query.order_by(column.desc())  # order by column in descending order
        else:
            query = query.order_by(column.asc())  # order by column in ascending order
    else:
        query = query.order_by(StudentDB.id)  # default order 

    start = (page - 1) * limit #page = 2 , limit = 2 -> start = 2
    students = query.offset(start).limit(limit).all()  # get the students for the current page

    return {
        "page": page,
        "limit": limit,
        "total_students": total_students,
        "students": students
    }


def _students_as_dict(students):
    return {
        student.id: StudentResponse.model_validate(student).model_dump()
        for student in students
    }


@app.get("/student", include_in_schema=False)
def get_all_legacy(db: Session = Depends(get_db)):
    return _students_as_dict(db.query(StudentDB).order_by(StudentDB.id).all())


@app.get("/paginate", include_in_schema=False)
def paginate_legacy(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    result = get_all(
        course=None,
        sort_by=None,
        order="asc",
        page=page,
        limit=limit,
        db=db,
    )
    return {
        **result,
        "students": [StudentResponse.model_validate(student).model_dump() for student in result["students"]],
    }


@app.get("/filter", include_in_schema=False)
def filter_legacy(course: str, db: Session = Depends(get_db)):
    students = db.query(StudentDB).filter(func.lower(StudentDB.course) == course.lower()).all()
    return _students_as_dict(students)


@app.get("/sort", include_in_schema=False)
def sort_legacy(
    sort_by: str,
    order: str = "asc",
    db: Session = Depends(get_db),
):
    result = get_all(
        course=None,
        sort_by=sort_by,
        order=order,
        page=1,
        limit=100,
        db=db,
    )
    return [StudentResponse.model_validate(student).model_dump() for student in result["students"]]


WEB_DIR = FilePath(__file__).resolve().parent / "web"
if not WEB_DIR.is_dir():
    WEB_DIR = FilePath(__file__).resolve().parent.parent / "web"
if WEB_DIR.is_dir():
    app.mount("/", StaticFiles(directory=WEB_DIR, html=True), name="web")
