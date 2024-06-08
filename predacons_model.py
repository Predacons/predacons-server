from dataclasses import dataclass

@dataclass
class PredaconsModel:
    model_name: str
    model_path: str
    trust_remote_code: bool
    use_fast_generation: bool
    draft_model_name: str
    model_bin:any
    tokenizer:any