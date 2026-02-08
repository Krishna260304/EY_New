from fastapi import APIRouter 
from pydantic import BaseModel 

router =APIRouter (prefix ="/chat",tags =["Chat"])

class ChatRequest (BaseModel ):
    message :str 

@router .post ("/reply")
def chat_reply (payload :ChatRequest ):
    return {"reply":f"You said: {payload .message }"}
