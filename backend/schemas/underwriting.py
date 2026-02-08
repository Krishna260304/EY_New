from pydantic import BaseModel 

class UnderwritingResult (BaseModel ):
    risk_score :float 
    approval_probability :float 
