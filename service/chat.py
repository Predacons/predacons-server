import json
from typing import List, Optional
from dataclasses import dataclass
from predacons_model import PredaconsModel
import predacons
import time
import random
import string
import os
import dotenv
from chat_class import Message, Conversation, ContentFilterResults, Choice, PromptFilterResults, Usage, ChatResponse,FilterCategory

dotenv.load_dotenv()

async def generate_cmpl_id():
    prefix = 'cmpl-'
    id_length = 22
    id_chars = string.ascii_letters + string.digits
    random_id = ''.join(random.choice(id_chars) for _ in range(id_length))
    return prefix + random_id

async def completions(conversation_body:str, model_dict, api_version:str = None):
    print("Entry Chat Completions")
    print(model_dict)    
    print(api_version)
    system_fingerprint = os.getenv('system_fingerprint')
    # print(conversation_body)
    
    # data = json.loads(conversation_body)
    conversation = Conversation(**conversation_body)

    print(conversation)
    # convert conversation.messages to a string
    message_str = ""
    for message in conversation.messages:
        message_str += message['role'] + " : " + message['content'] + "\n"
    message_str = message_str + "\n Assistant :"
    print(message_str)
    

    model = model_dict.model_bin
    tokenizer = model_dict.tokenizer
    trust_remote_code = model_dict.trust_remote_code
    fast_gen = model_dict.use_fast_generation
    draft_model = model_dict.draft_model_name
    print(model)
    print(tokenizer)

    output,tokenizer = predacons.generate(model = model,
        sequence = message_str,
        max_length = conversation.max_tokens,
        tokenizer = tokenizer,
        trust_remote_code = trust_remote_code)
    
    response = tokenizer.decode(output[0], skip_special_tokens=True)
    print(response)

    # response = "hello"
    filter_results = ContentFilterResults(
            hate = FilterCategory(filtered = False, severity = "safe"),
            self_harm = FilterCategory(filtered = False, severity = "safe"),
            sexual = FilterCategory(filtered = False, severity = "safe"),
            violence = FilterCategory(filtered = False, severity = "safe")
        )
    prompt_filter_results = PromptFilterResults(
        prompt_index = 0,
        content_filter_results = filter_results
    )
    choice = Choice(
        content_filter_results = filter_results,
        finish_reason = "length",
        index = 0,
        logprobs = None,
        message = Message(role = "assistant", content = response)
    )

    chat_response = ChatResponse(
        choices = [choice],
        created =  int(time.time()),
        id = await generate_cmpl_id(),
        model = model_dict.model_name,
        object = "chat.completion",
        prompt_filter_results = [prompt_filter_results],
        system_fingerprint = system_fingerprint,
        usage = Usage(completion_tokens = 1, prompt_tokens = 1, total_tokens = 1)
    )
    return chat_response