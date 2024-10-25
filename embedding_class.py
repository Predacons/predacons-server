from dataclasses import dataclass
from typing import List

@dataclass
class Embedding:
    object: str
    index: int
    embedding: List[float]

@dataclass
class Usage:
    prompt_tokens: int
    total_tokens: int

@dataclass
class EmbeddingResponse:
    object: str
    data: List[Embedding]
    model: str
    usage: Usage

@dataclass
class EmbeddingInput:
    input: List[str]
    user: str
    input_type: str

@dataclass
class EmbeddingInput:
    input: str
    user: str
    input_type: str