import torch
import constants
from transformers import AutoModelForCausalLM, AutoTokenizer

def load_local_llm():
    tokenizer = AutoTokenizer.from_pretrained(constants.STARCHAT_ALPHA)
    model = AutoModelForCausalLM.from_pretrained(constants.STARCHAT_ALPHA, device_map='auto',
                                         torch_dtype=torch.bfloat16,
                                         offload_folder="offload")

    return model, tokenizer

def create_source_code(prompt):
    model, tokenizer = load_local_llm()
    system_prompt = "<|system|>\nBelow is a conversation between a human and a coding model in Trapheus.<|end|>\n"
    user_prompt = f"<|user|>\n{prompt}<|end|>\n"
    assistant_prompt = "<|assistant|>"
    complete_prompt = system_prompt + user_prompt + assistant_prompt
    inputs = tokenizer.encode(complete_prompt, return_tensors="pt")
    outputs = model.generate(inputs,eos_token_id = 0,pad_token_id = 0,
                             max_length=256,
                             early_stopping=True)
    lex =  tokenizer.decode(outputs[0])
    lex = lex[len(complete_prompt):]
    if "<|end|>" in lex:
        cutoff = lex.find("<|end|>")
        lex = lex[:cutoff]
    return lex