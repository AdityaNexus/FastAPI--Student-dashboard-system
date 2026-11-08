from pydantic import BaseModel, Field , EmailStr , field_validator ,computed_field
from typing import Literal 
import json
class User(BaseModel):
    id : int = Field(..., description="The ID of the user")
    name : str = Field(..., description="The name of the user")
    class_ : str = Field(..., description="The class of the user")


#print(User.schema_json(indent=2))
# user = User(id=2, name="John Doe", class_="10th Grade")
# print(type(json.dumps((User.model_json_schema()))))
# print(json.dumps((User.model_json_schema()), indent=2))

class RuleStudent(BaseModel):
    name : str = Field(..., description="The name of the student") # ... means required field
    age : int = Field(..., description="The age of the student")
    marks : int = Field(..., description="The marks of the student")
    course : str = "python"
    phone : str = Field(..., description="The phone number of the student")



s = RuleStudent(name="Alice", age=20, marks=85, phone="123-456-7890")
# print(s.model_json_schema())
# print(type(s.model_json_schema()))
# print(s.model_dump_json(indent=2))
# print(type(s.model_dump_json(indent=2)))
# print(s.model_dump())
# print(type(s.model_dump()))



class EmailStudent(BaseModel):
    name : str 
    email : EmailStr



# s_e = EmailStudent(name="Bob", email="Aditya123@gmail.com")
# print(s_e.model_dump_json(indent=2))

""" field_validator"""


class Student(BaseModel):
    id : int = Field(...,examples = ["student_1"])
    name : str
    age : int = Field(..., ge = 0,le = 100, description="The age of the student")
    course : str = Field(..., description="The course of the student")
    email : EmailStr
    marks : int = Field(...,ge = 0,le = 100 , description="The marks of the student")

    # custom rule : Name only contain letters ans spaces
    @field_validator("name")  # field_validator is a decorator that is used to validate the field of the model
    @classmethod
    def check_name(cls, name : str):
        if not name.replace(" ", "").isalpha():
            raise ValueError("Name must only contain letters and spaces")
        return name.title()  # title() method is used to capitalize the first letter of each word in the name


    @computed_field  # computed_field is a decorator that is used to create a computed field in the model
    @property
    def graded(self)->str:
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


#s = Student(name="Alice Smith", id=1, age=20, course="Python", email="aditya123@gmail.com", marks=85)

#print(s.model_dump_json(indent=2))

""" Model Dump and Model Dump JSON """

# print(s.model_dump())  # model_dump() method is used to convert the model to a dictionary
# print(type(s.model_dump()))  # model_dump() method is used to convert the model to
if __name__ == "__main__":
    """Every student in our file will go through the Student Model"""
    with open("C:\\FastAPI\\revision\\student.json","r") as file :
        raw = json.load(file)
    #print(raw)


    for student_id , info in raw.items():
        s = Student(id = student_id,**info)
        print(s.model_dump(exclude={"id"}))  # exclude is used to exclude the field from the model_dump() method

