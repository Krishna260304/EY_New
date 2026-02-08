import os 
import joblib 
import numpy as np 

BASE_DIR =os .path .dirname (__file__ )
MODEL_PATH =os .path .join (BASE_DIR ,"persuasion_model.joblib")

try :
    _model =joblib .load (MODEL_PATH )
    MODEL_AVAILABLE =True 
except Exception as e :
    print (f"Warning: Could not load persuasion model: {e }. Using fallback.")
    _model =None 
    MODEL_AVAILABLE =False 

FEATURES =["intent_confidence","sentiment_score","urgency",
"hesitation","message_length"]

def predict_persuasion_score (
intent_confidence :float ,
sentiment_score :float ,
urgency :int ,
hesitation :int ,
message_length :int ,
):
    if not MODEL_AVAILABLE :

        score =(intent_confidence *0.3 +sentiment_score *0.3 +
        urgency *0.2 -hesitation *0.2 )

        if score >0.7 :
            bucket ="high"
        elif score >0.4 :
            bucket ="medium"
        else :
            bucket ="low"

        probs ={"high":0.33 ,"medium":0.33 ,"low":0.34 }
        probs [bucket ]=0.6 

        return {
        "conversion_bucket":bucket ,
        "probabilities":probs 
        }

    x =np .array ([[intent_confidence ,sentiment_score ,
    urgency ,hesitation ,message_length ]])
    proba =_model .predict_proba (x )[0 ]
    label =_model .classes_ [proba .argmax ()]

    return {
    "conversion_bucket":str (label ),
    "probabilities":{
    str (cls ):float (p )for cls ,p in zip (_model .classes_ ,proba )
    }
    }
