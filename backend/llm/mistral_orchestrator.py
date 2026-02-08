import os 
import torch 
import re 
import json 
from typing import Tuple ,Optional 
from transformers import AutoTokenizer ,AutoModelForCausalLM 
try :
    from transformers import BitsAndBytesConfig 
except Exception :
    BitsAndBytesConfig =None 
from utils .gpu_utils import get_device_manager ,setup_gpu_environment 


setup_gpu_environment ()
device_manager =get_device_manager ()



MODEL_ID =os .environ .get ("LLM_MODEL_ID","TinyLlama/TinyLlama-1.1B-Chat-v1.0")
MAX_NEW_TOKENS =int (os .environ .get ("LLM_MAX_TOKENS","128"))
DEVICE =device_manager .get_device ()
DTYPE =device_manager .get_dtype ()


_tokenizer :Optional [AutoTokenizer ]=None 
_model :Optional [AutoModelForCausalLM ]=None 


def _load_llm ()->Tuple [AutoTokenizer ,AutoModelForCausalLM ]:
    """Load tokenizer and model lazily with GPU-aware settings."""
    global _tokenizer ,_model 
    if _tokenizer is not None and _model is not None :
        return _tokenizer ,_model 

    _tokenizer =AutoTokenizer .from_pretrained (MODEL_ID ,use_fast =True )

    kwargs ={"torch_dtype":DTYPE ,"low_cpu_mem_usage":True }
    if str (DEVICE )=="cuda":

        if BitsAndBytesConfig is not None :
            bnb_config =BitsAndBytesConfig (
            load_in_4bit =True ,
            bnb_4bit_quant_type ="nf4",
            bnb_4bit_use_double_quant =True ,
            bnb_4bit_compute_dtype =torch .bfloat16 if hasattr (torch ,"bfloat16")else torch .float16 ,
            )
            kwargs ["quantization_config"]=bnb_config 
            kwargs ["device_map"]="auto"
        else :
            kwargs ["device_map"]="auto"

    try :
        _model =AutoModelForCausalLM .from_pretrained (MODEL_ID ,**kwargs )
    except Exception :

        fallback_kwargs ={"torch_dtype":DTYPE ,"low_cpu_mem_usage":True }
        if str (DEVICE )=="cuda":
            fallback_kwargs ["device_map"]="auto"
        _model =AutoModelForCausalLM .from_pretrained (MODEL_ID ,**fallback_kwargs )
    if str (DEVICE )!="cuda":
        _model .to (DEVICE )
    _model .eval ()
    return _tokenizer ,_model 


def mistral_think (context :str )->dict :
    """
    Mistral reasons over full context + tool results
    and returns a structured decision.
    """
    prompt =f"""
You are a senior banking AI assistant.

You are given analysis results from multiple AI tools.
Your task:
1. Talk naturally with the customer
2. Decide what options to offer next

Return ONLY JSON enclosed within <json>...</json> tags:
<json>
{{
    "reply": "...human friendly response...",
    "actions": ["apply_loan", "check_eligibility", "block_transaction", "upload_documents", "talk_to_human"],
    "confidence": 0.0
}}
</json>

Context:
{context }
"""

    tokenizer ,model =_load_llm ()
    inputs =tokenizer (prompt ,return_tensors ="pt").to (DEVICE )

    with torch .no_grad ():
        outputs =model .generate (
        **inputs ,
        max_new_tokens =MAX_NEW_TOKENS ,
        temperature =0.4 ,
        top_p =0.9 
        )

    text =tokenizer .decode (outputs [0 ],skip_special_tokens =True )


    def extract_first_json (s :str )->Optional [dict ]:

        tag_match =re .search (r"<json>(.*?)</json>",s ,re .DOTALL )
        candidates =[]
        if tag_match :
            candidates .append (tag_match .group (1 ))

        candidates .extend (re .findall (r"\{.*?\}",s ,re .DOTALL ))
        for c in candidates :
            try :
                return json .loads (c )
            except Exception :
                continue 
        return None 

    parsed =extract_first_json (text )
    if not parsed :
        return {
        "reply":"I understand. Let me help you step by step.",
        "actions":["talk_to_human"],
        "confidence":0.5 
        }
    return parsed 
