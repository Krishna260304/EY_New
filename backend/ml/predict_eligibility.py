import os 
import joblib 
import numpy as np 
from ml .gpu_accelerated_inference import accelerator 

BASE_DIR =os .path .dirname (__file__ )
MODEL_PATH =os .path .join (BASE_DIR ,"eligibility_model.joblib")

try :
    _model =joblib .load (MODEL_PATH )
    MODEL_AVAILABLE =True 
except Exception as e :
    print (f"Warning: Could not load eligibility model: {e }. Using fallback.")
    _model =None 
    MODEL_AVAILABLE =False 

def predict_eligibility (
credit_score :int ,
annual_income :float ,
employment_type :str ,
existing_loans_count :int ,
debt_to_income :float ,
intent_confidence :float ,
persuasion_index :float ,
sentiment_score :float ,
age :int ,
loan_amount :float ,
):
    if not MODEL_AVAILABLE :

        if credit_score >=700 and annual_income >=50000 and debt_to_income <0.4 :
            eligibility ="approved"
            probs ={"approved":0.8 ,"rejected":0.1 ,"review":0.1 }
        elif credit_score >=600 and annual_income >=30000 :
            eligibility ="review"
            probs ={"approved":0.3 ,"rejected":0.3 ,"review":0.4 }
        else :
            eligibility ="rejected"
            probs ={"approved":0.1 ,"rejected":0.7 ,"review":0.2 }

        return {"eligibility":eligibility ,"probabilities":probs }

    import pandas as pd 
    df =pd .DataFrame ([{
    "credit_score":credit_score ,
    "annual_income":annual_income ,
    "employment_type":employment_type ,
    "existing_loans_count":existing_loans_count ,
    "debt_to_income":debt_to_income ,
    "intent_confidence":intent_confidence ,
    "persuasion_index":persuasion_index ,
    "sentiment_score":sentiment_score ,
    "age":age ,
    "loan_amount":loan_amount 
    }])


    predictions ,proba_array =accelerator .predict_sklearn_model (_model ,df ,use_gpu =True )

    proba =proba_array [0 ]if proba_array is not None else None 
    classes =list (_model .classes_ )

    if proba is not None :
        best =classes [int (proba .argmax ())]
        return {"eligibility":best ,"probabilities":{c :float (p )for c ,p in zip (classes ,proba )}}
    else :

        return {"eligibility":"review","probabilities":{"approved":0.3 ,"rejected":0.3 ,"review":0.4 }}
