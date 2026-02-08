import os 
import joblib 
import pandas as pd 

BASE =os .path .dirname (__file__ )
MODEL =os .path .join (BASE ,"repayment_model.joblib")

try :
    clf =joblib .load (MODEL )
    MODEL_AVAILABLE =True 
except Exception as e :
    print (f"Warning: Could not load repayment model: {e }. Using fallback.")
    clf =None 
    MODEL_AVAILABLE =False 

THRESHOLD =0.4 

def predict_repayment (values ):
    if not MODEL_AVAILABLE :

        credit =values .get ("credit_score",700 )
        income =values .get ("annual_income",50000 )
        dti =values .get ("debt_to_income",0.3 )

        default_prob =0.2 
        if credit <600 :
            default_prob +=0.3 
        if dti >0.4 :
            default_prob +=0.2 
        if income <30000 :
            default_prob +=0.15 

        status ="risk_of_default"if default_prob >=THRESHOLD else "likely_to_repay"
        return {
        "default_probability":default_prob ,
        "repayment_status":status 
        }

    df =pd .DataFrame ([values ])
    proba =clf .predict_proba (df )[0 ][1 ]

    status ="risk_of_default"if proba >=THRESHOLD else "likely_to_repay"

    return {
    "default_probability":float (proba ),
    "repayment_status":status 
    }
