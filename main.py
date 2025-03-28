from fastapi import FastAPI, Query, HTTPException, status, Security,Depends, Request
from pydantic import BaseModel
from fastapi.security import APIKeyHeader, APIKeyQuery
from dotenv import load_dotenv
from predacons_model import PredaconsModel
import os
import service.chat as ChatService
import repo.predacons as PredaconsRepo
from fastapi.responses import StreamingResponse

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


@app.post("/openai/deployments/{model}/chat/completions", dependencies=[Depends(get_api_key)])
async def chat_completions(request: Request,model:str ,api_version:str = Query(default=None, alias="api-version")):
    body = await request.json()
    print("Entry Chat Completions")
    if model not in predacons_models:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Model {model} not found",
        )
    
    print(body)
    print(api_version)
    if body.get("stream"):
                return StreamingResponse(ChatService.completions_stream(body, predacons_models[model], api_version), media_type="text/event-stream")
    return await ChatService.completions(body, predacons_models[model], api_version)

@app.post("/openai/deployments/{model}/completions", dependencies=[Depends(get_api_key)])
async def nocontext_completions_endpoint(request: Request, model:str, api_version:str = Query(default=None, alias="api-version")):
    body = await request.json()
    print("Entry NoContext Completions Endpoint")
    if model not in predacons_models:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Model {model} not found",
        )
    
    print(body)
    print(model)
    print(api_version)
    return await ChatService.nocontext_completions(body, predacons_models[model], api_version)

@app.post("/openai/deployments/{model}/embeddings", dependencies=[Depends(get_api_key)])
async def embeddings_endpoint(request: Request,model:str, api_version:str = Query(default=None, alias="api-version")):
    body = await request.json()
    print("Entry Embeddings Endpoint")
    if model not in predacons_models:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Model {model} not found",
        )
    print(body)
    print(model)
    print(api_version)
    response = await ChatService.embeddings(body, predacons_models[model],model, api_version)
    return response
