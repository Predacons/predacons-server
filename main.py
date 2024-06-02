from fastapi import FastAPI, Query, HTTPException, status, Security,Depends, Request
from pydantic import BaseModel
from fastapi.security import APIKeyHeader, APIKeyQuery
import json
import service.chat as ChatService

with open('appSettings.json') as config_file:
    config = json.load(config_file)

API_KEYS = config['API_KEYS']

app = FastAPI()
api_key_query = APIKeyQuery(name="api-key", auto_error=False)
api_key_header = APIKeyHeader(name="api-key", auto_error=False)

def get_api_key(
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
def read_root():
    return {"Hello": "World"}

@app.post("/items/")
def create_item(item: Item):
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
async def create_item(request: Request,model:str ,api_version:str = Query(default=None, alias="api-version")):
    body = await request.json()
    print(body)
    print(model)
    print(api_version)
    return ChatService.completions(body, model, api_version)
