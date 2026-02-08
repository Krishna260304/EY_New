from fastapi import APIRouter 
from pydantic import BaseModel 
from typing import Dict ,Any ,Optional 

from fastapi .concurrency import run_in_threadpool 

from llm .mistral_orchestrator import mistral_think 
from ml .infer_intent import predict_intent 
from ml .infer_emotion import analyze_emotion 

from agents .sales_persuasion import analyze_message 
from agents .verification_agent import verify_documents 
from agents .underwriting_agent import underwrite_application 
from agents .risk_agent import assess_risk 
from agents .offer_generation_agent import generate_offer 
from agents .feedback_agent import generate_feedback 

import torch 
HF_DEVICE =0 if torch .cuda .is_available ()else -1 


router =APIRouter (prefix ="/orchestrator",tags =["Orchestrator"])


class OrchestratorRequest (BaseModel ):
    message :str 
    customer_id :Optional [str ]=None 
    application_data :Optional [Dict [str ,Any ]]=None 
    documents :Optional [Dict [str ,Any ]]=None 


@router .post ("/process")
async def master_orchestrator (payload :OrchestratorRequest ):
    text =payload .message 
    application_data =payload .application_data or {}
    documents =payload .documents or {}

    intent_result =await run_in_threadpool (predict_intent ,text )
    emotion_result =await run_in_threadpool (analyze_emotion ,text )

    sales =await analyze_message ({"message":text })

    doc_payload =dict (documents )
    if "name"not in doc_payload and application_data .get ("name"):
        doc_payload ["name"]=application_data ["name"]

    verification =(
    await run_in_threadpool (verify_documents ,doc_payload )if doc_payload else {}
    )
    underwriting =(
    await run_in_threadpool (underwrite_application ,application_data )
    if application_data 
    else {}
    )

    if application_data and verification and underwriting :
        risk =assess_risk (
        verification_result =verification ,
        underwriting_result =underwriting ,
        application_data =application_data ,
        )
    else :
        risk ={}

    if application_data and underwriting and risk :
        offer =generate_offer (
        application_data =application_data ,
        underwriting_result =underwriting ,
        risk_result =risk ,
        )
    else :
        offer ={}

    if verification and underwriting and risk :
        feedback =generate_feedback (
        verification_result =verification ,
        underwriting_result =underwriting ,
        risk_result =risk ,
        )
    else :
        feedback ={}

    context ={
    "user_message":text ,
    "customer_id":payload .customer_id ,
    "intent":intent_result ,
    "emotion":emotion_result ,
    "sales":sales ,
    "verification":verification ,
    "underwriting":underwriting ,
    "risk":risk ,
    "offer":offer ,
    "feedback":feedback ,
    "application_data":application_data ,
    "documents":documents ,
    }

    decision =mistral_think (str (context ))

    reply =None 
    actions =None 
    confidence =None 

    if isinstance (decision ,dict ):
        reply =decision .get ("reply")
        actions =decision .get ("actions")
        confidence =decision .get ("confidence")

    return {
    "assistant_reply":reply ,
    "actions":actions ,
    "confidence":confidence ,
    "signals":context ,
    }
