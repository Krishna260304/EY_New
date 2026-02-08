from fastapi import APIRouter 
from pydantic import BaseModel 

router =APIRouter (prefix ="/offers",tags =["Offer Mart"])

class OfferRequest (BaseModel ):
    user_id :str 
    category :str 

@router .post ("/get")
def get_offers (payload :OfferRequest ):
    offers ={
    "loan":["Personal Loan 10.5%","Home Loan 8.2%"],
    "insurance":["Health Insurance 2.1L","Life Cover 50L"],
    "credit_card":["Platinum Card","Gold Cashback Card"]
    }
    category =payload .category .lower ()
    return {
    "user_id":payload .user_id ,
    "offers":offers .get (category ,[])
    }
