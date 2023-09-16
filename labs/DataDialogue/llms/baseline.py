import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

def load_local_llm():
    tokenizer = AutoTokenizer.from_pretrained("HuggingFaceH4/starchat-alpha")
    model = AutoModelForCausalLM.from_pretrained("HuggingFaceH4/starchat-alpha",
                                                 load_in_8bit=True,
                                                 device_map='auto',
                                                 torch_dtype=torch.float16
                                                 )
    return model

