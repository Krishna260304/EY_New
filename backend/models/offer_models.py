from pydantic import BaseModel 

class OfferRequest (BaseModel ):
    user_id :str 
    category :str 
