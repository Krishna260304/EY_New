from transformers import pipeline 
import torch 

_model =None 

def _load ():
    global _model 
    if _model is None :
        device =0 if torch .cuda .is_available ()else -1 
        _model =pipeline (
        "text-classification",
        model ="distilbert-base-uncased",
        device =device 
        )
    return _model 

def predict_intent (text ):
    return _load ()(text )
