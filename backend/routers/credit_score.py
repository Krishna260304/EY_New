from fastapi import APIRouter 
from pydantic import BaseModel 

router =APIRouter (prefix ="/credit",tags =["Credit Score"])

class CreditRequest (BaseModel ):
    user_id :str 
    income :float 
    existing_loans :int 
    emi :float 

def calculate_credit_score (income :float ,existing_loans :int ,emi :float )->int :
    score =300 
    score +=income *0.01 
    score -=existing_loans *20 
    score -=emi *0.05 
    return max (300 ,min (int (score ),900 ))

@router .post ("/score")
def compute_credit_score (payload :CreditRequest ):
    score =calculate_credit_score (payload .income ,payload .existing_loans ,payload .emi )
    return {"user_id":payload .user_id ,"credit_score":score }
