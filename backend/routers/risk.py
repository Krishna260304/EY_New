from fastapi import APIRouter ,HTTPException 
from pydantic import BaseModel 
from ml .predict_risk import predict_risk 

router =APIRouter (
prefix ="/agent/risk",
tags =["Risk Scoring"]
)

class RiskInput (BaseModel ):
    credit_score :int 
    delinquency_12m :int 
    outstanding_debt :float 
    income :float 
    loan_amount :float 
    debt_to_income :float 
    age :int 
    num_hard_inquiries :int 
    employment_type :str 


class RiskOutput (BaseModel ):
    risk_tier :str 
    confidence :float 
    risk_score :int 


@router .post ("/score",response_model =RiskOutput )
async def score_risk (data :RiskInput ):
    try :
        result =predict_risk (data .model_dump ())
        return result 
    except Exception as e :
        raise HTTPException (
        status_code =500 ,
        detail =f"Risk scoring failed: {str (e )}"
        )

