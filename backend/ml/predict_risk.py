import os 
import joblib 
import pandas as pd 
import numpy as np 
import logging 
from ml .gpu_accelerated_inference import accelerator 

BASE_DIR =os .path .dirname (__file__ )
MODEL_PATH =os .path .join (BASE_DIR ,"risk_model.joblib")

TIER_MAP ={0 :"low",1 :"medium",2 :"high"}

logger =logging .getLogger (__name__ )

try :
    model =joblib .load (MODEL_PATH )
    MODEL_AVAILABLE =True 
    logger .info ("✓ Risk model loaded successfully")
except Exception as e :
    logger .warning (f"⚠ Risk model not available: {e }")
    model =None 
    MODEL_AVAILABLE =False 

def predict_risk (values ):
    if not MODEL_AVAILABLE :

        credit =values .get ("credit_score",700 )
        delinq =values .get ("delinquency_12m",0 )
        dti =values .get ("debt_to_income",0.3 )
        income =values .get ("annual_income",50000 )
        loan_amt =values .get ("loan_amount",10000 )


        lti =loan_amt /max (income ,1 )


        if credit >=750 and delinq ==0 and dti <=0.25 and lti <0.3 :
            tier ="low"
            pred_class =0 
            confidence =0.85 

        elif credit >=650 and delinq <=1 and dti <=0.40 and lti <0.5 :
            tier ="medium"
            pred_class =1 
            confidence =0.75 

        else :
            tier ="high"
            pred_class =2 
            confidence =0.70 

        risk_score =pred_class *50 
        probabilities ={"low":0.15 ,"medium":0.35 ,"high":0.50 }
        probabilities [tier ]=confidence 

        return {
        "risk_score":risk_score ,
        "risk_tier":tier ,
        "confidence":confidence ,
        "probabilities":probabilities 
        }

    df =pd .DataFrame ([values ])


    predictions ,pred_proba_array =accelerator .predict_sklearn_model (model ,df ,use_gpu =True )

    pred_class =int (predictions [0 ])
    pred_proba =pred_proba_array [0 ]if pred_proba_array is not None else None 

    if pred_proba is not None :
        confidence =float (pred_proba [pred_class ])
        probabilities ={TIER_MAP [i ]:float (p )for i ,p in enumerate (pred_proba )}
    else :
        confidence =0.75 
        probabilities ={"low":0.33 ,"medium":0.33 ,"high":0.34 }

    tier =TIER_MAP [pred_class ]
    risk_score =round (pred_class *50 )

    return {
    "risk_score":risk_score ,
    "risk_tier":tier ,
    "confidence":confidence ,
    "probabilities":probabilities 
    }
