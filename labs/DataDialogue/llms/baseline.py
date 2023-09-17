import torch
import constants
from transformers import AutoModelForCausalLM, AutoTokenizer

def load_local_llm():
    tokenizer = AutoTokenizer.from_pretrained(constants.STARCHAT_ALPHA)
    model = AutoModelForCausalLM.from_pretrained(constants.STARCHAT_ALPHA, device_map='auto',
                                         torch_dtype=torch.bfloat16,
                                         offload_folder="offload")

    return model, tokenizer

