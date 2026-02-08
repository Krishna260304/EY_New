import os 
import joblib 
import pandas as pd 

BASE =os .path .dirname (__file__ )
MODEL =os .path .join (BASE ,"offer_model.joblib")

try :
    bundle =joblib .load (MODEL )
    rate_model =bundle ["rate_model"]
    tenure_model =bundle ["tenure_model"]
    features =bundle ["features"]
    MODEL_AVAILABLE =True 
except Exception as e :
    print (f"Warning: Could not load offer model: {e }. Using fallback.")
    rate_model =None 
    tenure_model =None 
    features =None 
    MODEL_AVAILABLE =False 

VALID_TENURES =[12 ,24 ,36 ,48 ,60 ]

def recommend_offer (values ):
    if not MODEL_AVAILABLE :

        credit =values .get ("credit_score",700 )
        loan_amt =values .get ("loan_amount",10000 )
        income =values .get ("annual_income",50000 )


        if credit >=750 :
            rate =7.5 
        elif credit >=700 :
            rate =10.0 
        elif credit >=650 :
            rate =13.5 
        else :
            rate =18.0 


        if loan_amt <5000 :
            tenure =12 
        elif loan_amt <15000 :
            tenure =24 
        elif loan_amt <30000 :
            tenure =36 
        else :
            tenure =48 

        return {
        "recommended_rate":round (rate ,2 ),
        "recommended_tenure":tenure 
        }

    df =pd .DataFrame ([values ])[features ]

    rate =float (rate_model .predict (df )[0 ])
    rate =round (min (max (rate ,7.25 ),24.0 ),2 )

    raw_tenure =float (tenure_model .predict (df )[0 ])
    tenure =min (VALID_TENURES ,key =lambda x :abs (x -raw_tenure ))

    return {
    "recommended_rate":rate ,
    "recommended_tenure":int (tenure )
    }
