import json
from typing import List, Optional
from dataclasses import dataclass

@dataclass
class Message:
    role: str
    content: str

@dataclass
class Conversation:
    messages: List[Message]
    max_tokens: int
    temperature: float
    frequency_penalty: float
    presence_penalty: float
    top_p: float
    stop: Optional[str]

def completions(conversation_body:str, model:str, api_version:str = None):
    print("Entry Chat Completions")
    print(model)    
    print(api_version)
    # print(conversation_body)
    
    # data = json.loads(conversation_body)
    conversation = Conversation(**conversation_body)

    print(conversation)

    return {
        "choices": [
            {
                "finish_reason": "length",
                "index": 0,
                "logprobs": "hello",
                "text": "Hello, how can I help you today?"
            }
        ],
        "created": 1623196343,
        "id": "cmpl-3XQJ2bEg4sH4Vc7tQ8H0gB4X",
        "model": "gpt-3.5-turbo",
        "object": "text_completion",
        "prompt_filter_results": [],
        "system_fingerprint": "f9f7e3a3",
        "usage": {
            "completion": 1,
            "model": 1,
            "prompt": 1
        }
    }