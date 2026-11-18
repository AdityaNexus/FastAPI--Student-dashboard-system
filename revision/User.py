from fastapi import FastAPI, status, Form, File, UploadFile, Request
from pydantic import BaseModel, EmailStr ,Field
import hashlib
from typing import Annotated 
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
app = FastAPI()
import asyncio


class BaseUser(BaseModel):
    username: str
    email: EmailStr
    full_name: str | None = None




class UserIn(BaseUser):
    password: str


def paswordHasher(paas):
    return hashlib.sha256(paas).hexdigest()

class UserOut(BaseUser):
    pass


class UserInDB(BaseModel):
    username: str
    hashed_password: str
    email: EmailStr
    full_name: str | None = None

def save_user(user:UserIn):
    hased_pasword = paswordHasher(user.password)

class Item(BaseModel):
    name: str
    selling_price: float

db_items = [
    {"name": "Wireless Mouse", "selling_price": 1200.0, "cost_price": 650.0},
    {"name": "Mechanical Keyboard", "selling_price": 4500.0, "cost_price": 2800.0},
]

@app.get("/items/",response_model=list[Item],status_code=status.HTTP_200_OK)
def read_items():
    return db_items


# 1. this shows the webpage in your browser
# @app.get("/",response_class=HTMLResponse)
# def show_form_page():
#     return """
#     <html>
#         <body style="font-family: sans-serif; padding: 40px;">
#             <h2>Train Ticket Booking (HTML Form)</h2>
            
#             <!-- When you click Submit, the browser sends data to /book -->
#             <form action="/book" method="post">
#                 <label>Passenger Name:</label><br>
#                 <input type="text" name="passenger_name" required><br><br>

#                 <label>Age:</label><br>
#                 <input type="number" name="age" required><br><br>

#                 <input type="checkbox" name="window_seat">
#                 <label>Want Window Seat?</label><br><br>

#                 <button type="submit">Book Ticket</button>
#             </form>
#         </body>
#     </html>
#     """


# 2. THIS RECEIVES & VALIDATES THE FORM WHEN YOU CLICK SUBMIT
@app.post("/book")
async def book_ticket(
    passenger_name: Annotated[str, Form()],
    age: Annotated[int, Form()],
    window_seat: Annotated[bool, Form()] = False,
):
    # FastAPI unpacked the form data into normal Python variables!
    return {
        "status": "Ticket Confirmed!",
        "name": passenger_name,
        "age": age,
        "window_seat": window_seat,
    }

class StudentRegistrationForm(BaseModel):
    full_name: str = Field(min_length=3)
    email: EmailStr
    age: int = Field(ge=16, le=100)  # Must be between 16 and 100
    course: str
    agree_terms: bool = False  # Defaults to False if checkbox is unchecked

@app.get("/", response_class=HTMLResponse)
async def show_registration_page():
    return """
    <html>
        <body style="font-family: sans-serif; padding: 40px; max-width: 450px;">
            <h2>AI Engineering Bootcamp</h2>

            <form id="regForm">
                <label>Full Name:</label><br>
                <input type="text" name="full_name" required style="width: 100%; padding: 6px;"><br><br>

                <label>Email:</label><br>
                <input type="email" name="email" required style="width: 100%; padding: 6px;"><br><br>

                <label>Age (16+):</label><br>
                <input type="number" name="age" required style="width: 100%; padding: 6px;"><br><br>

                <label>Course Track:</label><br>
                <select name="course" style="width: 100%; padding: 6px;">
                    <option value="FastAPI & Backend">FastAPI & Backend</option>
                    <option value="LLM & AI Agents">LLM & AI Agents</option>
                </select><br><br>

                <button type="submit" style="padding: 10px 16px; cursor: pointer;">Register Now</button>
            </form>

            <!-- Hidden UI card where FastAPI's JSON response will be displayed -->
            <div id="resultBox" style="display: none; margin-top: 20px; padding: 15px; border-radius: 6px;"></div>

            <script>
                document.getElementById("regForm").addEventListener("submit", async function(e) {
                    e.preventDefault(); // 1. Stop browser from jumping to /register

                    // 2. Pack form inputs and send quietly to FastAPI in the background
                    const formData = new FormData(this);
                    const response = await fetch("/register", {
                        method: "POST",
                        body: formData
                    });

                    // 3. Parse the JSON returned by FastAPI
                    const data = await response.json();
                    const resultBox = document.getElementById("resultBox");
                    resultBox.style.display = "block";

                    // 4. Use the JSON fields to build real UI elements
                    if (response.ok) {
                        resultBox.style.backgroundColor = "#e6f4ea";
                        resultBox.style.border = "1px solid #34a853";
                        resultBox.innerHTML = `
                            <h3 style="margin-top: 0; color: #137333;">✅ ${data.status}</h3>
                            <p><strong>Student:</strong> ${data.student_name}</p>
                            <p><strong>Enrolled Course:</strong> ${data.selected_course}</p>
                            <p><strong>Confirmation ID:</strong> #${data.enrollment_id}</p>
                        `;
                        this.reset(); // Clear the form inputs
                    } else {
                        // Show Pydantic validation errors nicely if age < 16 or name too short
                        resultBox.style.backgroundColor = "#fce8e6";
                        resultBox.style.border = "1px solid #d93025";
                        resultBox.innerHTML = `<p style="color: #c5221f;">❌ Error: ${data.detail[0].msg}</p>`;
                    }
                });
            </script>
        </body>
    </html>
    """


# 2. BACKEND API (Pure data processing, returns JSON)
@app.post("/register")
async def register_student(form_data: Annotated[StudentRegistrationForm, Form()]):
    return {
        "status": "Enrollment Confirmed",
        "student_name": form_data.full_name,
        "selected_course": form_data.course,
        "enrollment_id": 1042,
    }

@app.get("/file", response_class=HTMLResponse)
def show_uploaded_page():
    return """
    <html>
        <body style="font-family: sans-serif; padding: 40px; max-width: 480px;">
            <h2>Upload Document to FastAPI</h2>

            <form id="uploadForm">
                <label>Choose any file (Image, PDF, TXT):</label><br><br>
                <!-- `name="uploaded_file"` must match the FastAPI parameter name -->
                <input type="file" name="uploaded_file" required><br><br>

                <button type="submit" style="padding: 10px 16px; cursor: pointer;">Upload File</button>
            </form>

            <div id="resultBox" style="display: none; margin-top: 20px; padding: 15px; border-radius: 6px;"></div>

            <script>
                document.getElementById("uploadForm").addEventListener("submit", async function(e) {
                    e.preventDefault(); // Stay on the same page

                    // FormData automatically packs the selected binary file as multipart/form-data
                    const formData = new FormData(this);

                    const response = await fetch("/upload/", {
                        method: "POST",
                        body: formData
                    });

                    const data = await response.json();
                    const resultBox = document.getElementById("resultBox");
                    resultBox.style.display = "block";
                    resultBox.style.backgroundColor = "#e6f4ea";
                    resultBox.style.border = "1px solid #34a853";

                    resultBox.innerHTML = `
                        <h3 style="margin-top: 0; color: #137333;">✅ File Received!</h3>
                        <p><strong>File Name:</strong> ${data.filename}</p>
                        <p><strong>File Type:</strong> ${data.content_type}</p>
                        <p><strong>Size:</strong> ${data.file_size_bytes} bytes</p>
                    `;
                });
            </script>
        </body>
    </html>
    """

class FileException(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


@app.exception_handler(FileException)
async def file_exception_handler(_request: Request, exc: FileException):
    return JSONResponse(status_code=400, content={"detail": exc.message})


@app.post("/upload/")
async def handle_file_upload(uploaded_file: UploadFile | None = File(default=None)):
    if uploaded_file is None or not uploaded_file.filename:
        raise FileException("No file was uploaded.")

    contents = await uploaded_file.read()  # Read the file contents into memory
    if not contents:
        raise FileException("The uploaded file is empty.")

    return {
        "filename": uploaded_file.filename,
        "content_type": uploaded_file.content_type,
        "file_size_bytes": len(contents),
    }

