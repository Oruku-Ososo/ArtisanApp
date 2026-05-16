from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging
import core

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

app = FastAPI(
    title="Greeting & Computation Service",
    description="A simple API for greetings and math operations.",
    version="1.0.0"
)

class GreetRequest(BaseModel):
    name: str

class AddRequest(BaseModel):
    a: float
    b: float

@app.get("/")
async def root():
    return {"message": "Welcome to the Greeting & Computation Service!"}

@app.post("/greet")
async def create_greeting(request: GreetRequest):
    try:
        message = core.greet(request.name)
        logging.info(f"Generated greeting for: {request.name}")
        return {"greeting": message}
    except ValueError as e:
        logging.error(f"Greeting error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/add")
async def compute_addition(request: AddRequest):
    result = core.add_numbers(request.a, request.b)
    logging.info(f"Computed addition: {request.a} + {request.b} = {result}")
    return {"result": result}
