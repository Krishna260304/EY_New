from pydantic import BaseModel 

class CRMRequest (BaseModel ):
    customer_name :str 
    query :str 
