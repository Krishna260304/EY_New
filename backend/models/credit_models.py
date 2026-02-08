from pydantic import BaseModel 

class CreditRequest (BaseModel ):
    user_id :str 
    income :float 
    existing_loans :int 
    emi :float 
