from fastapi import APIRouter 
from typing import Dict 

from agents .feedback_agent import generate_feedback 

router =APIRouter (
prefix ="/feedback",
tags =["Feedback"]
)


@router .post ("/")
async def feedback_endpoint (payload :Dict ):
    return generate_feedback (
    verification_result =payload .get ("verification_result",{}),
    underwriting_result =payload .get ("underwriting_result",{}),
    risk_result =payload .get ("risk_result",{})
    )
