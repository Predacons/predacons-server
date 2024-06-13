import predacons
import os
import time
from predacons_model import PredaconsModel

def str2bool(v):
  return v.lower() in ("yes", "true", "t", "1")

async def load_model(model_name:str):
    try:
        start_time = time.time()
        print(f"Loading model {model_name}")

        path = os.getenv(model_name+"_path")
        if path is None:
            print(f"{model_name}_path not found")
            return f"{model_name}_path not found"
        
        trust_remote_code = str2bool(os.getenv(model_name+"_trust_remote_code"))
        if trust_remote_code is None:
            print(f"{model_name}_trust_remote_code not found so setting to False")
            trust_remote_code = False
        
        use_fast_generation = str2bool(os.getenv(model_name+"_use_fast_generation"))
        if use_fast_generation is None:
            print(f"{model_name}_use_fast_generation not found so setting to False")
            use_fast_generation = False
        
        draft_model_name = None
        if use_fast_generation == True:
            draft_model_name = os.getenv(model_name+"_draft_model_name")
            if draft_model_name is None:
                print(f"{model_name}_draft_model_name not found using primary model as draft model")
                draft_model_name = path
        
        model = predacons.load_model(
            model_path = path,
            trust_remote_code=trust_remote_code,
            use_fast_generation=use_fast_generation,
            draft_model_name=draft_model_name
        ) 
          
        # tokenizers = AutoTokenizer.from_pretrained(path)
        tokenizers = predacons.load_tokenizer(path) #Updated

        # model = model_name + path
        # tokenizers = model_name + "tokenizer"
        predacons_model = PredaconsModel(model_name, path, trust_remote_code, use_fast_generation, draft_model_name, model, tokenizers)
        print(f"Model {model_name} loaded: {model}")
        print(f"Tokenizer {model_name} loaded: {tokenizers}")
        end_time = time.time()
        print(f"Model {model_name} loaded successfully in {end_time - start_time} seconds.")
        return predacons_model
    except Exception as e:
        print(f"An error occurred while loading the model: {e}")
        return None

    
async def load_models():
    print("Loading models...")
    # load model list from env 
    model_list = os.getenv('model_list')
    if model_list is not None:
        model_list = model_list.split(',')
    else:
        print("model_list not found")
        model_list = []
    print(model_list)
    # load models
    models = {}
    for model in model_list:
        print(f"Loading model {model}")
        predacons_model = await load_model(model)
        if predacons_model is not None:
            models[model] = predacons_model
    return models