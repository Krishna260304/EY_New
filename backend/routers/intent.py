from fastapi import APIRouter 
from pydantic import BaseModel 
from ml .intent_inference import ensemble 

router =APIRouter ()

class IntentRequest (BaseModel ):
    text :str 

@router .post ("/predict")
def predict_intent (req :IntentRequest ):
    return ensemble .predict (req .text )
