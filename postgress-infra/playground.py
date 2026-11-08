from dotenv import load_dotenv
import os
load_dotenv()  # take environment variables from .env.
DATABASE_URL = os.getenv("DATABASE_URL")
from sqlalchemy import create_engine , text ,Column ,String , Integer
from sqlalchemy.orm import sessionmaker , DeclarativeBase
import json
from pathlib import Path

#print(f"Database URL: {DATABASE_URL}")
# create engine = the road to the database
# .all() -> every row
#.first() -> first row
#.scalar() -> first column of the first row
engine = create_engine(DATABASE_URL)
with engine.connect() as conn:
    version = conn.execute(text("SELECT version();"))
   # print(f"Database version {version.fetchone()[0]}")


#Step 4: Session = One visit , open visit , open , dso work , commit , close 
"""
A session is a way to interact with the database. It's like a single visit to the database.
DeclarativeBase is the Parent class from sqlalchemy that turn the normal python class into a database table.
Declarative : you declare(describe) what a table looks like 
Base        : Its the parent class everything else built on top of this.
"""

class Base(DeclarativeBase):
    pass

class StudentDB(Base):
    __tablename__ = "student_records"
    id      = Column(String, primary_key=True)
    name    = Column(String(50), nullable=False)
    age     = Column(Integer, nullable=False)
    course  = Column(String(50), nullable=False)
    email   = Column(String, unique=True, nullable=False)  
    marks   = Column(Integer, nullable=False)

#bind = engine -> attach to : create the table in the database if it doesn't exist
Base.metadata.create_all(bind=engine)  # create the table in the database if it doesn't exist

# creating Session : A session is a way to interact with the database.
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()  # create a session to interact with the database

def get_data(path):
    with open(path,"r") as file :
        data = json.load(file)
    return data

def load_in_database(data):
    for student_id, student in data.items():
        if db.get(StudentDB , student_id) is None:
            db.add(StudentDB(id = student_id,
                             name = student["name"],
                             age = student["age"],
                             course = student["course"],
                             email = student["email"],
                             marks = student["marks"]))
    db.commit()  # commit the changes to the database

# if db.get(StudentDB , "001") is None:
#     db.add(StudentDB(id ="001",
#                      name = "aditya",
#                      age = 20,
#                      course = "Btech",
#                      email = "aditya@example.com",
#                      marks = 90))
#     db.commit()  # commit the changes to the database


# Read it Back 

# for i in db.query(StudentDB).all():
#     print(f"ID: {i.id}, Name: {i.name}, Age: {i.age}, Course: {i.course}, Email: {i.email}, Marks: {i.marks}")


#update 

# aditya  = db.get(StudentDB , "001")
# print(f"Before Update: ID: {aditya.id}, Name: {aditya.name}, Age: {aditya.age}, Course: {aditya.course}, Email: {aditya.email}, Marks: {aditya.marks}")

# aditya.name = "Aditya"
# aditya.age = 21
# aditya.marks = 95

# db.commit()

# print(f"After Update: ID: {aditya.id}, Name: {aditya.name}, Age: {aditya.age}, Course: {aditya.course}, Email: {aditya.email}, Marks: {aditya.marks}")
if __name__ == "__main__":
    # user = Path(input("Enter the path of the student.json file: "))
    # data = get_data(user)
    # load_in_database(data)
    for i in db.query(StudentDB).all():
        print(f"ID: {i.id}, Name: {i.name}, Age: {i.age}, Course: {i.course}, Email: {i.email}, Marks: {i.marks}")