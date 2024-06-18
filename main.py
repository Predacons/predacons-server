from fastapi import FastAPI, Query, HTTPException, status, Security,Depends, Request
from pydantic import BaseModel, ValidationError
from fastapi.security import APIKeyHeader, APIKeyQuery
from dotenv import load_dotenv
from predacons_model import PredaconsModel
import os
import service.chat as ChatService
import repo.predacons as PredaconsRepo
import json

load_dotenv()
predacons_models = {}

API_KEYS = os.getenv('API_KEYS')
if API_KEYS is not None:
    API_KEYS = API_KEYS.split(',')
else:
    print("API_KEYS not found")
    API_KEYS = []

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    print("lifespan Startup")
    print("Setting up...")
    print("loading models for startup...")
    # Load models
    global predacons_models
    predacons_models = await PredaconsRepo.load_models()
    print(predacons_models)
    # Load tokenizers
   

@app.on_event("shutdown")
async def shutdown_event():
    print("Cleaning up...")
    print("Closing models...")
    # Close models
    global predacons_models
    predacons_models = None

api_key_query = APIKeyQuery(name="api-key", auto_error=False)
api_key_header = APIKeyHeader(name="api-key", auto_error=False)

async def get_api_key(
    api_key_query: str = Security(api_key_query),
    api_key_header: str = Security(api_key_header),
) -> str:
    if api_key_query in API_KEYS:
        return api_key_query
    if api_key_header in API_KEYS:
        return api_key_header
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing API Key",
    )

class Item(BaseModel):
    name: str
    description: str = None
    price: float
    tax: float = None

@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.post("/items/")
async def create_item(item: Item):
    return item

class Item(BaseModel):
    choices: list
    created: int
    id: str 
    model: str
    object: str
    prompt_filter_results: list
    system_fingerprint: str
    usage: dict

@app.post("/deployments/{model}/chat/completions", dependencies=[Depends(get_api_key)])
async def chat_completions(request: Request, model: str, api_version: str = Query(default=None, alias="api-version")):
    try:
        body = await request.json()
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON format",
        )
    
    try:
        if model not in predacons_models:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Model {model} not found",
            )
        
        return await ChatService.completions(body, predacons_models[model], api_version)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


