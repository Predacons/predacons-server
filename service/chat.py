import json
from typing import List, Optional
from dataclasses import dataclass
from predacons_model import PredaconsModel
import predacons
from chat_class import Message, Conversation, ContentFilterResults, Choice, PromptFilterResults, Usage, Response



async def completions(conversation_body:str, model_dict, api_version:str = None):
    print("Entry Chat Completions")
    print(model_dict)    
    print(api_version)
    # print(conversation_body)
    
    # data = json.loads(conversation_body)
    conversation = Conversation(**conversation_body)

    print(conversation)
    

    model = model_dict.model_bin
    tokenizer = model_dict.tokenizer
    trust_remote_code = model_dict.trust_remote_code
    fast_gen = model_dict.use_fast_generation
    draft_model = model_dict.draft_model_name
    print(model)
    print(tokenizer)

    # output,tokenizer = predacons.generate(model = model,
    #     sequence = conversation.messages,
    #     max_length = conversation.max_tokens,
    #     tokenizer = tokenizer,
    #     trust_remote_code = trust_remote_code)
    #  response = tokenizer.decode(output[0], skip_special_tokens=True)
    #  print(response)

    response = "hello"
    
    chat = Choice(
        content_filter_results = ContentFilterResults(filtered = False, severity = "low"),
        finish_reason = "length",
        index = 0,
        logprobs = response,
        message = Message(role = "system", content = response)
    )
    return chat
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