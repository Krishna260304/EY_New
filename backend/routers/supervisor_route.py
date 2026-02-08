import os 
import joblib 
import numpy as np 
from fastapi import APIRouter 

BASE =os .path .dirname (os .path .dirname (__file__ ))
MODEL =os .path .join (BASE ,"ml","supervisor_model.joblib")

bundle =joblib .load (MODEL )

vec =bundle ["vectorizer"]
clf =bundle ["classifier"]

CONFIDENCE_THRESHOLD =0.7 

router =APIRouter (prefix ="/supervisor",tags =["Supervisor"])


@router .post ("/route")
def route_message (data :dict ):
    text =data ["text"].lower ().strip ()
    X =vec .transform ([text ])

    probs =clf .predict_proba (X )[0 ]
    best_idx =int (np .argmax (probs ))
    confidence =float (probs [best_idx ])
    route =clf .classes_ [best_idx ]

    if confidence <CONFIDENCE_THRESHOLD :
        route ="human"

    return {
    "route":route ,
    "confidence":round (confidence ,3 )
    }
