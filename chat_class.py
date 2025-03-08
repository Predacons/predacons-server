from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Message:
    role: Optional[str]
    content: Optional[str]

@dataclass
class Conversation:
    messages: List[Message]
    max_tokens: int = 500
    temperature: float = 0.7
    frequency_penalty: float = None
    presence_penalty: float = None
    top_p: float = None
    stop: Optional[str] = None
    model: Optional[str] = None
    encoding_format: str = None

    def __init__(self, **kwargs):
        valid_keys = {field.name for field in self.__dataclass_fields__.values()}
        filtered_kwargs = {k: v for k, v in kwargs.items() if k in valid_keys}
        for key, value in filtered_kwargs.items():
            setattr(self, key, value)

@dataclass
class FilterCategory:
    filtered: bool
    severity: str

@dataclass
class ContentFilterResults:
    hate: FilterCategory
    self_harm: FilterCategory
    sexual: FilterCategory
    violence: FilterCategory

@dataclass
class Choice:
    content_filter_results: ContentFilterResults
    finish_reason: str
    index: int
    logprobs: Optional[str]
    delta: Optional[Message] = None
    message: Optional[Message] = None

@dataclass
class PromptFilterResults:
    prompt_index: int
    content_filter_results: ContentFilterResults

@dataclass
class Usage:
    completion_tokens: int
    prompt_tokens: int
    total_tokens: int

@dataclass
class ChatResponse:
    choices: List[Choice]
    created: int
    id: str
    model: str
    object: str
    prompt_filter_results: List[PromptFilterResults]
    system_fingerprint: str
    usage: Usage