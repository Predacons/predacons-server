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
from embedding_class import Embedding, Usage as embedding_usage, EmbeddingResponse,EmbeddingInput

dotenv.load_dotenv()

async def generate_cmpl_id():
    prefix = 'cmpl-'
    id_length = 22
    id_chars = string.ascii_letters + string.digits
    random_id = ''.join(random.choice(id_chars) for _ in range(id_length))
    return prefix + random_id

async def completions(conversation_body:str, model_dict, api_version:str = None):
    print("Entry Chat Completions")
    print(api_version)
    system_fingerprint = os.getenv('system_fingerprint')
    # print(conversation_body)
    
    # data = json.loads(conversation_body)
    conversation = Conversation(**conversation_body)

    print(conversation)
    
    model = model_dict.model_bin
    tokenizer = model_dict.tokenizer
    trust_remote_code = model_dict.trust_remote_code
    fast_gen = model_dict.use_fast_generation
    draft_model = model_dict.draft_model_name

    response = predacons.chat_generate(model = model,
            sequence = conversation.messages,
            max_length = conversation.max_tokens,
            tokenizer = tokenizer,
            trust_remote_code = trust_remote_code,
            do_sample=True,   
            temperature = conversation.temperature,
            dont_print_output = True,
            )
    
    print(response)

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

async def generate_cmpl_id():
    prefix = 'cmpl-'
    id_length = 22
    id_chars = string.ascii_letters + string.digits
    random_id = ''.join(random.choice(id_chars) for _ in range(id_length))
    return prefix + random_id

async def completions_stream(conversation_body: str, model_dict, api_version: str = None):
    print("Entry Chat Completions Stream")
    print(api_version)
    system_fingerprint = os.getenv('system_fingerprint')
    
    conversation = Conversation(**conversation_body)
    print(conversation)
    
    model = model_dict.model_bin
    tokenizer = model_dict.tokenizer
    trust_remote_code = model_dict.trust_remote_code
    fast_gen = model_dict.use_fast_generation
    draft_model = model_dict.draft_model_name

    thread, stream = predacons.chat_generate(
        model=model,
        sequence=conversation.messages,
        max_length=conversation.max_tokens,
        tokenizer=tokenizer,
        trust_remote_code=trust_remote_code,
        do_sample=True,
        temperature=conversation.temperature,
        dont_print_output=True,
        stream=True
    )
    
    thread.start()
    
    for response in stream:
        filter_results = ContentFilterResults(
            hate=FilterCategory(filtered=False, severity="safe"),
            self_harm=FilterCategory(filtered=False, severity="safe"),
            sexual=FilterCategory(filtered=False, severity="safe"),
            violence=FilterCategory(filtered=False, severity="safe")
        )
        prompt_filter_results = PromptFilterResults(
            prompt_index=0,
            content_filter_results=filter_results
        )
        choice = Choice(
            content_filter_results=filter_results,
            finish_reason=None,
            index=0,
            logprobs=None,
            delta=Message(role="assistant", content=response)
        )

        chat_response = ChatResponse(
            choices=[choice],
            created=int(time.time()),
            id=await generate_cmpl_id(),
            model=model_dict.model_name,
            object="chat.completion.chunk",
            prompt_filter_results=[prompt_filter_results],
            system_fingerprint=system_fingerprint,
            usage=Usage(completion_tokens=1, prompt_tokens=1, total_tokens=1)
        )
        
        chat_response_json = json.dumps(chat_response, default=lambda o: o.__dict__)
        yield f"data: {chat_response_json}\n\n"

    yield "data: [DONE]\n\n"

async def nocontext_completions(conversation_body:str, model_dict, api_version:str = None):
    print("Entry NoContext Completions")
    print(api_version)
    system_fingerprint = os.getenv('system_fingerprint')
    
    current_message = conversation_body["messages"][-1]

    conversation = Conversation(
        messages=[Message(role=current_message["role"], content=current_message["content"])],
        max_tokens=conversation_body["max_tokens"],
        temperature=conversation_body["temperature"],
        frequency_penalty=conversation_body["frequency_penalty"],
        presence_penalty=conversation_body["presence_penalty"],
        top_p=conversation_body["top_p"],
        stop=conversation_body["stop"]
    )

    print(conversation)

    message_str = current_message['role'] + " : " + current_message['content'] + "\n Assistant :"
    print(message_str)

    model = model_dict.model_bin
    tokenizer = model_dict.tokenizer
    trust_remote_code = model_dict.trust_remote_code
    fast_gen = model_dict.use_fast_generation
    draft_model = model_dict.draft_model_name

    output,tokenizer = predacons.generate(model = model,
        sequence = message_str,
        max_length = conversation.max_tokens,
        tokenizer = tokenizer,
        trust_remote_code = trust_remote_code)
    
    response = tokenizer.decode(output[0], skip_special_tokens=True)
    print(response)

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

async def embeddings(body, model_dict,model, api_version:str = None):
    print("Entry Embeddings")
    print(api_version)

    embedding_input = EmbeddingInput(**body)

    embeddings_object = model_dict
    embeddings = embeddings_object.get_embedding(embedding_input.input)
    if type(embedding_input.input) == str:
        embeddings = [embeddings]
    # convert embeddings to list of Embedding objects
    embeddings_list = []
    for i, embedding in enumerate(embeddings):
        embeddings_list.append(Embedding(object = "embedding", index = i, embedding = embedding))

    usage = embedding_usage(prompt_tokens = len(embeddings_list), total_tokens = len(embeddings_list))
    embedding_response = EmbeddingResponse(object = "list", data = embeddings_list, model = model, usage = usage)
    return embedding_response
    
