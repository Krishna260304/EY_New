from fastapi import APIRouter 
from pydantic import BaseModel 
from typing import Dict 
from ml .predict_eligibility import predict_eligibility 

router =APIRouter (prefix ="/agent/eligibility",tags =["Eligibility"])

class EligibilityRequest (BaseModel ):
    credit_score :int 
    annual_income :float 
    employment_type :str 
    existing_loans_count :int 
    debt_to_income :float 
    intent_confidence :float 
    persuasion_index :float 
    sentiment_score :float 
    age :int 
    loan_amount :float 

@router .post ("/check")
async def check (req :EligibilityRequest )->Dict :
    out =predict_eligibility (
    credit_score =req .credit_score ,
    annual_income =req .annual_income ,
    employment_type =req .employment_type ,
    existing_loans_count =req .existing_loans_count ,
    debt_to_income =req .debt_to_income ,
    intent_confidence =req .intent_confidence ,
    persuasion_index =req .persuasion_index ,
    sentiment_score =req .sentiment_score ,
    age =req .age ,
    loan_amount =req .loan_amount ,
    )
    return out 
