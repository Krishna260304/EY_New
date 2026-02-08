import os 
import joblib 
import numpy as np 

BASE =os .path .dirname (__file__ )
MODEL =os .path .join (BASE ,"supervisor_model.joblib")

bundle =joblib .load (MODEL )

vec =bundle ["vectorizer"]
clf =bundle ["classifier"]

CONFIDENCE_THRESHOLD =0.35 

def normalize (text :str )->str :
    return " ".join (text .lower ().strip ().split ())

def route_message (text :str ):
    text =normalize (text )
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
