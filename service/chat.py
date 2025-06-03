import json
from typing import List, Optional
from dataclasses import dataclass
from predacons_model import PredaconsModel
import predacons
import time
import random
import string
import os
import uuid
import dotenv
from chat_class import Message, Conversation, ContentFilterResults, Choice, PromptFilterResults, Usage, ChatResponse, FilterCategory, ToolCall,Tool
from embedding_class import Embedding, Usage as embedding_usage, EmbeddingResponse,EmbeddingInput

dotenv.load_dotenv()

async def generate_cmpl_id():
    prefix = 'cmpl-'
    id_length = 22
    id_chars = string.ascii_letters + string.digits
    random_id = ''.join(random.choice(id_chars) for _ in range(id_length))
    return prefix + random_id

async def generate_tool_id():
    prefix = 'call-'
    id_length = 22
    id_chars = string.ascii_letters + string.digits
    random_id = ''.join(random.choice(id_chars) for _ in range(id_length))
    return prefix + random_id

async def completions(conversation_body:str, model_dict, api_version:str = None):
    print("Entry Chat Completions")
    print(api_version)
    system_fingerprint = os.getenv('system_fingerprint')
    
    conversation = Conversation(**conversation_body)

    print(conversation)
    
    model = model_dict.model_bin
    tokenizer = getattr(model_dict, 'tokenizer', None)
    processor = getattr(model_dict, 'processor', None)
    trust_remote_code = model_dict.trust_remote_code
    fast_gen = model_dict.use_fast_generation
    draft_model = model_dict.draft_model_name

    # Check if tools are present in the request and if tool_choice is 'auto' or has a specific function
    if conversation.tool_choice is None:
        conversation.tool_choice = 'auto'
    has_tools = conversation.tools is not None and len(conversation.tools) > 0
    use_tools = has_tools and (
        conversation.tool_choice in ['auto', 'any'] or 
        (conversation.tool_choice is not None and 
         ((hasattr(conversation.tool_choice, 'type') and conversation.tool_choice.type == 'function') or 
          (isinstance(conversation.tool_choice, dict) and conversation.tool_choice.get('type') == 'function'))
        )
    )
    
    # Craft a special instruction if tools are being used
    if has_tools and use_tools:
        # Create a system instruction that explains the tools
        tool_instructions = """You have access to some tools that can be called to get the answer. 
        it is is up to up if you need to use the tool or not. But if you choose to use the tool make sure to respond in a very strict format.
        The format is as follows:
        ```json
        {
            "tool_use":true,
            "name": "tool_name",
            "arguments": {

            }
        }
        ```
        You have access to the following tools:\n"""
        
        for tool in conversation.tools:
            if hasattr(tool, 'type') and tool.type == "function":
                if hasattr(tool, 'function'):
                    func = tool.function
                    tool_instructions += f"- {func.name}: {func.description}\n"
                    
                    # Add parameters information if available
                    if hasattr(func, 'parameters'):
                        tool_instructions += f"  Parameters:\n"
                        if hasattr(func.parameters, 'properties'):
                            for param_name, param in func.parameters.properties.items():
                                required = "Required" if hasattr(func.parameters, 'required') and param_name in func.parameters.required else "Optional"
                                param_type = param.type if hasattr(param, 'type') else ""
                                param_desc = param.description if hasattr(param, 'description') else ""
                                tool_instructions += f"    - {param_name} ({param_type}): {param_desc} [{required}]\n"
                                
                                # Add enum values if available
                                if hasattr(param, 'enum'):
                                    enum_values = ", ".join([str(v) for v in param.enum])
                                    tool_instructions += f"      Allowed values: [{enum_values}]\n"
            elif isinstance(tool, dict) and tool.get('type') == "function":
                if 'function' in tool:
                    func = tool['function']
                    tool_instructions += f"- {func['name']}: {func['description']}\n"
                    
                    # Add parameters information if available
                    if 'parameters' in func:
                        tool_instructions += f"  Parameters:\n"
                        if 'properties' in func['parameters']:
                            for param_name, param in func['parameters']['properties'].items():
                                required = "Required" if 'required' in func['parameters'] and param_name in func['parameters']['required'] else "Optional"
                                param_type = param.get('type', "")
                                param_desc = param.get('description', "")
                                tool_instructions += f"    - {param_name} ({param_type}): {param_desc} [{required}]\n"
                                
                                # Add enum values if available
                                if 'enum' in param:
                                    enum_values = ", ".join([str(v) for v in param['enum']])
                                    tool_instructions += f"      Allowed values: [{enum_values}]\n"
        
        # Add the tool instructions to the messages if there isn't already a system message
        has_system_message = any(
            (hasattr(message, 'role') and message.role == "system") or 
            (isinstance(message, dict) and message.get('role') == "system") 
            for message in conversation.messages
        )
        
        if has_system_message:
            # Append tool instructions to the existing system message
            for i, message in enumerate(conversation.messages):
                if (hasattr(message, 'role') and message.role == "system") or (isinstance(message, dict) and message.get('role') == "system"):
                    # Handle both object and dict case
                    if hasattr(message, 'content'):
                        conversation.messages[i].content = message.content + "\n\n" + tool_instructions
                    elif isinstance(message, dict) and 'content' in message:
                        message['content'] = message['content'] + "\n\n" + tool_instructions
                    break
        else:
            # Add a new system message with tool instructions
            system_message = Message(role="system", content=tool_instructions)
            conversation.messages.insert(0, system_message)

    response = predacons.chat_generate(
        model = model,
        sequence = conversation.messages,
        max_length = conversation.max_tokens,
        tokenizer = tokenizer,
        processor = processor,
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
    
    # Check if response contains tool calls
    tool_calls = None
    message_content = response
    if has_tools and use_tools and ("```json" in response or "{" in response):
        try:
            # Try to extract JSON from the response if it's in a code block
            if "```json" in response:
                json_content = response.split("```json")[1].split("```")[0].strip()
            elif "{" in response and "}" in response:
                start_idx = response.find("{")
                end_idx = response.rfind("}") + 1
                json_content = response[start_idx:end_idx].strip()
            else:
                json_content = None
                
            if json_content:
                # Parse the JSON content
                parsed_json = json.loads(json_content)
                
                # Check if it's a tool call format
                if isinstance(parsed_json, dict) and "name" in parsed_json and "arguments" in parsed_json:
                    # Create a proper tool call
                    tool_calls = [
                        ToolCall(
                            id=await generate_tool_id(),
                            type="function",
                            function={
                                "name": parsed_json["name"],
                                "arguments": json.dumps(parsed_json["arguments"])
                            }
                        )
                    ]
                    # Set message content to null when using tool calls
                    message_content = None
        except Exception as e:
            print(f"Error parsing tool call: {e}")
            # If we can't parse it as a tool call, treat it as regular content
            tool_calls = None
    
    choice = Choice(
        content_filter_results = filter_results,
        finish_reason = "stop" if tool_calls else "length",
        index = 0,
        logprobs = None,
        message = Message(role="assistant", content=message_content, tool_calls=tool_calls)
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

async def completions_stream(conversation_body: str, model_dict, api_version: str = None):
    print("Entry Chat Completions Stream")
    print(api_version)
    system_fingerprint = os.getenv('system_fingerprint')
    
    conversation = Conversation(**conversation_body)
    print(conversation)
    
    model = model_dict.model_bin
    tokenizer = getattr(model_dict, 'tokenizer', None)
    processor = getattr(model_dict, 'processor', None)
    trust_remote_code = model_dict.trust_remote_code
    fast_gen = model_dict.use_fast_generation
    draft_model = model_dict.draft_model_name

    if conversation.tool_choice is None:
        conversation.tool_choice = 'auto'
    # Check if tools are present in the request and if tool_choice is 'auto' or has a specific function
    has_tools = conversation.tools is not None and len(conversation.tools) > 0
    use_tools = has_tools and (
        conversation.tool_choice in ['auto', 'any'] or 
        (conversation.tool_choice is not None and 
         ((hasattr(conversation.tool_choice, 'type') and conversation.tool_choice.type == 'function') or 
          (isinstance(conversation.tool_choice, dict) and conversation.tool_choice.get('type') == 'function'))
        )
    )
    
    # Craft a special instruction if tools are being used
    if has_tools and use_tools:
        # Create a system instruction that explains the tools
        tool_instructions = """You have access to some tools that can be called to get the answer. 
        it is is up to up if you need to use the tool or not. But if you choose to use the tool make sure to respond in a very strict format.
        The format is as follows:
        ```json
        {
            "tool_use":true,
            "name": "tool_name",
            "arguments": {
                
            }
        }
        ```
        You have access to the following tools:\n"""
        
        for tool in conversation.tools:
            if hasattr(tool, 'type') and tool.type == "function":
                if hasattr(tool, 'function'):
                    func = tool.function
                    tool_instructions += f"- {func.name}: {func.description}\n"
                    
                    # Add parameters information if available
                    if hasattr(func, 'parameters'):
                        tool_instructions += f"  Parameters:\n"
                        if hasattr(func.parameters, 'properties'):
                            for param_name, param in func.parameters.properties.items():
                                required = "Required" if hasattr(func.parameters, 'required') and param_name in func.parameters.required else "Optional"
                                param_type = param.type if hasattr(param, 'type') else ""
                                param_desc = param.description if hasattr(param, 'description') else ""
                                tool_instructions += f"    - {param_name} ({param_type}): {param_desc} [{required}]\n"
                                
                                # Add enum values if available
                                if hasattr(param, 'enum'):
                                    enum_values = ", ".join([str(v) for v in param.enum])
                                    tool_instructions += f"      Allowed values: [{enum_values}]\n"
            elif isinstance(tool, dict) and tool.get('type') == "function":
                if 'function' in tool:
                    func = tool['function']
                    tool_instructions += f"- {func['name']}: {func['description']}\n"
                    
                    # Add parameters information if available
                    if 'parameters' in func:
                        tool_instructions += f"  Parameters:\n"
                        if 'properties' in func['parameters']:
                            for param_name, param in func['parameters']['properties'].items():
                                required = "Required" if 'required' in func['parameters'] and param_name in func['parameters']['required'] else "Optional"
                                param_type = param.get('type', "")
                                param_desc = param.get('description', "")
                                tool_instructions += f"    - {param_name} ({param_type}): {param_desc} [{required}]\n"
                                
                                # Add enum values if available
                                if 'enum' in param:
                                    enum_values = ", ".join([str(v) for v in param['enum']])
                                    tool_instructions += f"      Allowed values: [{enum_values}]\n"
        
        # Add the tool instructions to the messages if there isn't already a system message
        has_system_message = any(
            (hasattr(message, 'role') and message.role == "system") or 
            (isinstance(message, dict) and message.get('role') == "system") 
            for message in conversation.messages
        )
        
        if has_system_message:
            # Append tool instructions to the existing system message
            for i, message in enumerate(conversation.messages):
                if (hasattr(message, 'role') and message.role == "system") or (isinstance(message, dict) and message.get('role') == "system"):
                    # Handle both object and dict case
                    if hasattr(message, 'content'):
                        conversation.messages[i].content = message.content + "\n\n" + tool_instructions
                    elif isinstance(message, dict) and 'content' in message:
                        message['content'] = message['content'] + "\n\n" + tool_instructions
                    break
        else:
            # Add a new system message with tool instructions
            system_message = Message(role="system", content=tool_instructions)
            conversation.messages.insert(0, system_message)

    thread, stream = predacons.chat_generate(
        model=model,
        sequence=conversation.messages,
        max_length=conversation.max_tokens,
        tokenizer=tokenizer,
        processor=processor,
        trust_remote_code=trust_remote_code,
        do_sample=True,
        temperature=conversation.temperature,
        dont_print_output=True,
        stream=True
    )
    
    thread.start()
    
    # Buffer to accumulate response for potential tool call detection
    response_buffer = ""
    stream_id = await generate_cmpl_id()
    
    for response in stream:
        response_buffer += response
        
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
        
        # Check if accumulated response might contain a tool call
        tool_call_detected = has_tools and use_tools and (
            "```json" in response_buffer or 
            ('{' in response_buffer and '}' in response_buffer)
        )
        
        if tool_call_detected and (response_buffer.endswith('}') or response_buffer.endswith('```')):
            try:
                # Try to extract JSON from the response
                if "```json" in response_buffer:
                    json_content = response_buffer.split("```json")[1].split("```")[0].strip()
                elif "{" in response_buffer and "}" in response_buffer:
                    start_idx = response_buffer.find("{")
                    end_idx = response_buffer.rfind("}") + 1
                    json_content = response_buffer[start_idx:end_idx].strip()
                else:
                    json_content = None
                
                if json_content:
                    # Parse the JSON to see if it's a valid tool call
                    parsed_json = json.loads(json_content)
                    
                    if isinstance(parsed_json, dict) and "name" in parsed_json and "arguments" in parsed_json:
                        # Create a proper tool call
                        tool_call = ToolCall(
                            id=await generate_tool_id(),
                            type="function",
                            function={
                                "name": parsed_json["name"],
                                "arguments": json.dumps(parsed_json["arguments"])
                            }
                        )
                        
                        # Send the tool call as a special message
                        choice = Choice(
                            content_filter_results=filter_results,
                            finish_reason="tool_calls",
                            index=0,
                            logprobs=None,
                            message=Message(role="assistant", content=None, tool_calls=[tool_call])
                        )
                        
                        chat_response = ChatResponse(
                            choices=[choice],
                            created=int(time.time()),
                            id=stream_id,
                            model=model_dict.model_name,
                            object="chat.completion.chunk",
                            prompt_filter_results=[prompt_filter_results],
                            system_fingerprint=system_fingerprint,
                            usage=Usage(completion_tokens=1, prompt_tokens=1, total_tokens=1)
                        )
                        
                        chat_response_json = json.dumps(chat_response, default=lambda o: o.__dict__)
                        yield f"data: {chat_response_json}\n\n"
                        
                        # Clear the buffer after sending a tool call
                        response_buffer = ""
                        continue
            except Exception as e:
                print(f"Error parsing potential tool call in stream: {e}")
                # Continue with normal streaming if parsing fails
                
        # Normal streaming for text content
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
            id=stream_id,
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
    tokenizer = getattr(model_dict, 'tokenizer', None)
    processor = getattr(model_dict, 'processor', None)
    trust_remote_code = model_dict.trust_remote_code
    fast_gen = model_dict.use_fast_generation
    draft_model = model_dict.draft_model_name

    # Choose which to pass: tokenizer or processor
    output, _ = predacons.generate(model = model,
        sequence = message_str,
        max_length = conversation.max_tokens,
        tokenizer = tokenizer,
        processor = processor,
        trust_remote_code = trust_remote_code)
    # Use processor.decode if tokenizer is None
    if tokenizer is not None:
        response = tokenizer.decode(output[0], skip_special_tokens=True)
    else:
        response = processor.decode(output, skip_special_tokens=True)
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

