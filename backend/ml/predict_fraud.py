import os 
import joblib 
import pandas as pd 
from ml .gpu_accelerated_inference import accelerator 

BASE =os .path .dirname (__file__ )
MODEL =os .path .join (BASE ,"fraud_model.joblib")

try :
    _model_data =joblib .load (MODEL )
    iso =_model_data ["isolation_forest"]
    scaler =_model_data .get ("scaler")
    clf =_model_data ["classifier"]
    MODEL_AVAILABLE =True 
except Exception as e :
    print (f"Warning: Could not load fraud model: {e }. Using fallback.")
    iso =None 
    scaler =None 
    clf =None 
    MODEL_AVAILABLE =False 

def detect_fraud (values ):
    if not MODEL_AVAILABLE :

        num_inquiries =values .get ("num_hard_inquiries",0 )
        delinq =values .get ("delinquency_12m",0 )
        credit =values .get ("credit_score",700 )

        fraud_score =0.0 
        if num_inquiries >5 :
            fraud_score +=0.3 
        if delinq >2 :
            fraud_score +=0.3 
        if credit <500 :
            fraud_score +=0.2 

        verdict ="fraudulent"if fraud_score >0.5 else "legit"
        return {"fraud_probability":fraud_score ,"status":verdict }

    df =pd .DataFrame ([values ])

    X =df .copy ()
    X ["anomaly_score"]=iso .predict (X )

    if scaler :
        X_scaled =scaler .transform (X )
    else :
        X_scaled =X .values 


    X_scaled_df =pd .DataFrame (X_scaled )
    predictions ,proba_array =accelerator .predict_sklearn_model (clf ,X_scaled_df ,use_gpu =True )

    prob =proba_array [0 ][1 ]if proba_array is not None else 0.5 
    verdict ="fraudulent"if prob >0.5 else "legit"
    return {"fraud_probability":float (prob ),"status":verdict }
