
from fastapi import APIRouter 
from pydantic import BaseModel 
from typing import Dict ,Any ,Optional 
import re 

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

router =APIRouter (prefix ="/orchestrator",tags =["Orchestrator"])


INTENT_LABEL_MAP ={
"LABEL_0":"BUSINESS_LOAN_REQUEST",
"LABEL_1":"PERSONAL_LOAN_REQUEST",
"LABEL_2":"GENERAL_INQUIRY",
"LABEL_3":"COMPLAINT",
"LABEL_4":"DOCUMENT_QUERY"
}


RISK_DECISION_ACTIONS ={
"LOW":{
"APPROVED":["offer","confirm","apply_loan"],
"REVIEW":["check_eligibility","upload_documents"],
"DECLINED":["explain_reason","talk_to_human"]
},
"MEDIUM":{
"APPROVED":["upload_documents","check_eligibility"],
"REVIEW":["upload_documents","check_eligibility","clarify_intent"],
"DECLINED":["explain_reason","talk_to_human"]
},
"HIGH":{
"APPROVED":["upload_documents","recheck"],
"REVIEW":["upload_documents","talk_to_human"],
"DECLINED":["explain_reason","talk_to_human"]
}
}

def mask_sensitive_data (data :str ,data_type :str ="aadhaar")->str :
    """Mask sensitive information like Aadhaar and PAN."""
    if not data :
        return data 

    data_str =str (data )
    if data_type =="aadhaar"and len (data_str )>=12 :
        return f"{data_str [:4 ]}-XXXX-XXXX"
    elif data_type =="pan"and len (data_str )>=10 :
        return f"{data_str [:4 ]}****{data_str [-1 ]}"
    return data_str 

def map_intent_label (intent_result :Any )->Dict :
    """Map LABEL_X to meaningful business intent."""
    if not intent_result :
        return {"label":"UNKNOWN","score":0.0 }

    if isinstance (intent_result ,list )and len (intent_result )>0 :
        first =intent_result [0 ]
        if isinstance (first ,dict ):
            label =first .get ("label","LABEL_0")
            score =first .get ("score",0.0 )
            mapped_label =INTENT_LABEL_MAP .get (label ,label )
            return {"label":mapped_label ,"score":score ,"original_label":label }

    return {"label":"UNKNOWN","score":0.0 }

def generate_empathetic_reply (
verification_result :Dict ,
underwriting_result :Dict ,
risk_result :Dict ,
emotion :str ,
intent_conf :float 
)->str :
    """Generate emotion-aware empathetic reply."""


    ver_status =verification_result .get ("status")
    if ver_status !="verified":
        ver_reason =verification_result .get ("reason","document verification issue")
        if emotion in ["sadness","fear","concern"]:
            return (
            f"I understand this is important to you. Your application is almost complete, "
            f"but we couldn't verify your documents due to: {ver_reason }. "
            "Please re-upload a valid document so we can continue evaluating your loan eligibility."
            )
        else :
            return (
            f"Your application is almost complete. We couldn't verify your documents due to: {ver_reason }. "
            "Please re-upload a valid document so we can continue."
            )


    decision =underwriting_result .get ("decision")
    risk_band =risk_result .get ("risk_band")

    if decision =="APPROVED"and risk_band =="LOW":
        return "Great news! Your application looks strong. Let me show you the offers available."
    elif decision =="REVIEW":
        if emotion in ["sadness","fear","concern"]:
            return (
            "I can see you're eager to proceed. We need to review a few more details before "
            "we can finalize your application. This is a standard process to ensure we offer you the best terms."
            )
        else :
            return "We need to review a few more details before finalizing your application. This is standard procedure."
    elif decision =="DECLINED":
        reasons =underwriting_result .get ("reasons",[])
        reason_text =", ".join (reasons )if reasons else "policy constraints"
        return (
        f"I understand this may be disappointing. Unfortunately, we're unable to approve the loan at this time "
        f"due to: {reason_text }. Our team can discuss alternative options with you."
        )


    if intent_conf <0.55 :
        return "I'd like to help you better. Could you tell me more about what kind of loan you're looking for?"

    return "Thank you for your application. Let me check the details and guide you through the next steps."


class OrchestratorRequest (BaseModel ):
    message :str 
    customer_id :Optional [str ]=None 
    application_data :Optional [Dict [str ,Any ]]=None 
    documents :Optional [Dict [str ,Any ]]=None 


def _compute_overall_confidence (
intent_confidence :Optional [float ],
verification :Dict [str ,Any ],
underwriting :Dict [str ,Any ],
risk :Dict [str ,Any ],
offer :Dict [str ,Any ],
)->float :
    scores =[]

    if intent_confidence and intent_confidence >0 :
        if intent_confidence <0.55 :
            scores .append (intent_confidence *0.5 )
        else :
            scores .append (intent_confidence )

    v_conf =verification .get ("confidence")if isinstance (verification ,dict )else None 
    if v_conf :
        scores .append (float (v_conf ))

    uw_decision =underwriting .get ("decision")if isinstance (underwriting ,dict )else None 
    if uw_decision :
        scores .append ({"APPROVED":0.85 ,"REVIEW":0.55 ,"DECLINED":0.25 }.get (uw_decision ,0.5 ))

    risk_band =risk .get ("risk_band")if isinstance (risk ,dict )else None 
    if risk_band :
        scores .append ({"LOW":0.78 ,"MEDIUM":0.48 ,"HIGH":0.2 }.get (risk_band ,0.4 ))

    risk_score =risk .get ("risk_score")if isinstance (risk ,dict )else None 
    if isinstance (risk_score ,(int ,float ))and risk_score >0 :
        normalized =risk_score /100.0 if risk_score >1 else risk_score 
        scores .append (max (0.1 ,1 -normalized *0.7 ))

    if isinstance (offer ,dict ):
        if offer .get ("offer_available")is True :
            scores .append (0.78 )
        elif offer :
            scores .append (0.35 )

    if not scores :
        return 0.5 
    avg =round (sum (scores )/len (scores ),2 )
    if underwriting .get ("decision")=="REVIEW"or risk .get ("risk_band")=="MEDIUM":
        return max (0.55 ,min (avg ,0.65 ))
    return avg 


@router .post ("/process")
async def master_orchestrator (payload :OrchestratorRequest ):
    text =payload .message 
    application_data =payload .application_data or {}
    documents =payload .documents or {}


    intent_result =await run_in_threadpool (predict_intent ,text )
    emotion_result =await run_in_threadpool (analyze_emotion ,text )


    mapped_intent =map_intent_label (intent_result )

    sales =await analyze_message ({"message":text })


    doc_payload =dict (documents )
    if "name"not in doc_payload and application_data .get ("name"):
        doc_payload ["name"]=application_data ["name"]

    verification =(
    await run_in_threadpool (verify_documents ,doc_payload )if doc_payload else {}
    )



    if verification .get ("status")=="verified"and application_data :
        underwriting =await run_in_threadpool (underwrite_application ,application_data )
    elif application_data and not verification :

        underwriting =await run_in_threadpool (underwrite_application ,application_data )
    else :

        underwriting ={
        "decision":"PENDING",
        "risk":"UNKNOWN",
        "emi_ratio":0.0 ,
        "credit_score":application_data .get ("credit_score",0 ),
        "reasons":["Verification must pass before underwriting"]
        }


    if application_data and verification and underwriting :
        risk =assess_risk (
        verification_result =verification ,
        underwriting_result =underwriting ,
        application_data =application_data ,
        )
    else :
        risk ={}

    if (
    application_data 
    and underwriting 
    and risk 
    and (verification .get ("status")=="verified")
    and (underwriting .get ("decision")=="APPROVED")
    and (risk .get ("risk_band")!="HIGH")
    ):
        offer =generate_offer (
        application_data =application_data ,
        underwriting_result =underwriting ,
        risk_result =risk ,
        )
    else :

        blocked_by =None 
        retry_allowed =True 

        if not verification or verification .get ("status")!="verified":
            blocked_by ="DOCUMENT_VERIFICATION"
            reason ="Offer gated: document verification required"
        elif underwriting .get ("decision")!="APPROVED":
            blocked_by ="UNDERWRITING"
            reason =f"Offer gated: underwriting decision is {underwriting .get ('decision','PENDING')}"
            if underwriting .get ("decision")=="DECLINED":
                retry_allowed =False 
        elif risk .get ("risk_band")=="HIGH":
            blocked_by ="RISK_ASSESSMENT"
            reason ="Offer gated: high risk profile"
            retry_allowed =False 
        else :
            blocked_by ="INCOMPLETE_DATA"
            reason ="Offer gated: incomplete application data"

        offer ={
        "offer_available":False ,
        "blocked_by":blocked_by ,
        "retry_allowed":retry_allowed ,
        "reason":reason 
        }


    emotion_label =None 
    emotion_score =None 
    if isinstance (emotion_result ,dict ):
        emotion_label =emotion_result .get ("emotion")or emotion_result .get ("label")
        emotion_score =float (emotion_result .get ("score")or 0.0 )
    elif isinstance (emotion_result ,list )and emotion_result :
        first =emotion_result [0 ]
        if isinstance (first ,dict ):
            emotion_label =first .get ("emotion")or first .get ("label")
            emotion_score =float (first .get ("score")or 0.0 )
        elif isinstance (first ,list ):
            best =max (
            [d for d in first if isinstance (d ,dict )],
            key =lambda d :float (d .get ("score")or 0.0 ),
            default =None ,
            )
            if best :
                emotion_label =best .get ("emotion")or best .get ("label")
                emotion_score =float (best .get ("score")or 0.0 )


    is_declined_high =(
    underwriting .get ("decision")=="DECLINED"
    and risk .get ("risk_band")=="HIGH"
    )

    if is_declined_high :

        emotion_label ="neutral"
        emotion_score =emotion_score or 0.5 
        emotion_result ={"emotion":"neutral","score":float (emotion_score )}


    if verification and underwriting and risk :

        feedback =generate_feedback (
        verification_result =verification ,
        underwriting_result =underwriting ,
        risk_result =risk ,
        emotion =emotion_label 
        )
    else :
        feedback ={}

    if sales :
        sentiment_block =sales .get ("sentiment")or {}
        if sentiment_block .get ("score",0.0 )==0.0 and emotion_score :
            sentiment_block ["score"]=emotion_score 
            if emotion_label :
                sentiment_block ["label"]=str (emotion_label ).upper ()
        if emotion_score and not sentiment_block .get ("label")and emotion_label :
            sentiment_block ["label"]=str (emotion_label ).upper ()
        if sentiment_block :
            sales ["sentiment"]=sentiment_block 

        emotion_block =sales .get ("emotion_analysis")or {}
        if emotion_block .get ("score",0.0 )==0.0 and emotion_score :
            emotion_block ["score"]=emotion_score 
        if not emotion_block .get ("emotion")and emotion_label :
            emotion_block ["emotion"]=emotion_label 
        if emotion_block :
            sales ["emotion_analysis"]=emotion_block 
            if not emotion_result :
                emotion_result ={"emotion":emotion_block .get ("emotion"),"score":emotion_block .get ("score")}


        if mapped_intent and mapped_intent .get ("label"):
            sales ["intent"]=mapped_intent .get ("label")

        if is_declined_high :

            emotion_label ="neutral"
            emotion_score =emotion_score or 0.5 
            emotion_result ={"emotion":"neutral","score":float (emotion_score )}
            sentiment_block =sales .get ("sentiment")or {}
            sentiment_block ["label"]="NEGATIVE"
            sentiment_block ["score"]=max (0.75 ,float (sentiment_block .get ("score",0.0 )or 0.0 ))
            sales ["sentiment"]=sentiment_block 


    if isinstance (risk ,dict ):
        risk_score_val =risk .get ("risk_score")
        if isinstance (risk_score_val ,(int ,float ))and risk_score_val >0.95 :
            risk ["risk_score"]=0.95 
            if isinstance (risk .get ("risk_score_percent"),(int ,float )):
                risk ["risk_score_percent"]=95 


    masked_app_data =dict (application_data )if application_data else {}
    if "aadhaar"in masked_app_data :
        masked_app_data ["aadhaar"]=mask_sensitive_data (masked_app_data ["aadhaar"],"aadhaar")
    if "pan"in masked_app_data :
        masked_app_data ["pan"]=mask_sensitive_data (masked_app_data ["pan"],"pan")

    masked_docs =dict (documents )if documents else {}
    if "aadhaar"in masked_docs :
        masked_docs ["aadhaar"]=mask_sensitive_data (masked_docs ["aadhaar"],"aadhaar")
    if "pan"in masked_docs :
        masked_docs ["pan"]=mask_sensitive_data (masked_docs ["pan"],"pan")

    emotion_payload =emotion_result 
    if emotion_label :
        emotion_payload ={"emotion":emotion_label ,"score":float (emotion_score or 0.0 )}
    if is_declined_high :

        emotion_payload ={"emotion":"neutral","score":float (emotion_score or 0.5 )}
        if isinstance (sales ,dict ):
            sales ["emotion_analysis"]={"emotion":"neutral","score":float (emotion_score or 0.5 )}
            sales ["sentiment"]={
            "label":"NEGATIVE",
            "score":max (0.75 ,float (sales .get ("sentiment",{}).get ("score",0.0 )or 0.0 ))
            }

    context ={
    "user_message":text ,
    "customer_id":payload .customer_id ,
    "intent":mapped_intent ,
    "emotion":emotion_payload ,
    "sales":sales ,
    "verification":verification ,
    "underwriting":underwriting ,
    "risk":risk ,
    "offer":offer ,
    "feedback":feedback ,
    "application_data":masked_app_data ,
    "documents":masked_docs ,
    }

    decision =mistral_think (str (context ))

    reply =None 
    actions =None 
    confidence =None 

    if isinstance (decision ,dict ):
        reply =decision .get ("reply")
        actions =decision .get ("actions")
        confidence =decision .get ("confidence")


    intent_conf =mapped_intent .get ("score",0.0 )


    if not reply or len (reply )<20 :
        reply =generate_empathetic_reply (
        verification ,
        underwriting ,
        risk ,
        emotion_label or "neutral",
        intent_conf 
        )


    if is_declined_high :
        applicant_name =application_data .get ("name")if application_data else None 
        name_prefix =f", {applicant_name }"if applicant_name else ""
        reply =(
        f"I understand you are looking for a loan{name_prefix }. After reviewing your application, "
        "we are unable to approve the loan at this time due to a high repayment burden and a low credit score. "
        "If you would like, our support team can walk you through alternative options or steps to improve eligibility."
        )


    actions =actions or []


    if "block_transaction"in actions :

        fraud_score =application_data .get ("fraud_score",0.0 )if application_data else 0.0 
        if fraud_score <0.7 :
            actions =[a for a in actions if a !="block_transaction"]


    if "talk_to_human"in actions :
        if underwriting .get ("decision")not in ["DECLINED"]and risk .get ("risk_band")!="HIGH":
            actions =[a for a in actions if a !="talk_to_human"]


    risk_band =risk .get ("risk_band","MEDIUM")
    uw_decision =underwriting .get ("decision","PENDING")

    if risk_band in RISK_DECISION_ACTIONS and uw_decision in RISK_DECISION_ACTIONS [risk_band ]:
        allowed_actions =RISK_DECISION_ACTIONS [risk_band ][uw_decision ]

        filtered_actions =[]
        for action in actions :
            if action in allowed_actions or action in ["clarify_intent","check_eligibility"]:
                filtered_actions .append (action )
        actions =filtered_actions if filtered_actions else allowed_actions [:2 ]


    if intent_conf <0.55 and not is_declined_high :
        actions =[a for a in actions if a !="apply_loan"]
        if "clarify_intent"not in actions :
            actions .insert (0 ,"clarify_intent")


    final_approval =(
    underwriting .get ("decision")=="APPROVED"
    and offer .get ("offer_available")is True 
    and risk .get ("risk_band")=="LOW"
    )

    if final_approval and intent_conf >=0.55 :
        actions =[a for a in actions if a !="clarify_intent"]
        if "apply_loan"not in actions :
            actions .insert (0 ,"apply_loan")


    if verification .get ("status")=="failed"and "upload_documents"not in actions :
        actions .insert (0 ,"upload_documents")


    if uw_decision =="REVIEW"and "check_eligibility"not in actions :
        if "upload_documents"in actions :
            actions .insert (1 ,"check_eligibility")
        else :
            actions .append ("check_eligibility")


    if is_declined_high :
        actions =["talk_to_human"]


    if not confidence or confidence ==0 :
        confidence =_compute_overall_confidence (
        intent_conf if sales else None ,
        verification ,
        underwriting ,
        risk ,
        offer ,
        )


    decision_confidence =confidence 
    if underwriting .get ("decision")!="APPROVED"or risk .get ("risk_band")in {"MEDIUM","HIGH"}:
        decision_confidence =max (0.40 ,min (float (confidence or 0.6 ),0.60 ))
    elif verification .get ("status")=="failed":
        decision_confidence =max (0.35 ,min (float (confidence or 0.5 ),0.55 ))

    if is_declined_high and verification .get ("status")=="verified":
        decision_confidence =max (float (decision_confidence or 0.0 ),0.85 )


    reply_confidence =intent_conf if intent_conf >0 else 0.5 
    if emotion_score and emotion_score >0.6 :
        reply_confidence =min (0.95 ,reply_confidence +0.1 )


    if is_declined_high :
        if not isinstance (feedback ,dict ):
            feedback ={}
        feedback ["tone_applied"]="supportive_neutral"
        feedback ["feedback"]=(
        "We are unable to approve this request because your current loan repayments take up a large "
        "portion of your income, and your credit score is below the required threshold."
        )


    response_signals =dict (context )
    if (
    response_signals .get ("underwriting",{}).get ("decision")=="DECLINED"
    and response_signals .get ("risk",{}).get ("risk_band")=="HIGH"
    ):
        response_signals ["emotion"]={"emotion":"neutral","score":float (emotion_score or 0.5 )}
        if isinstance (response_signals .get ("sales"),dict ):
            response_sales =dict (response_signals ["sales"])
            response_sales ["sentiment"]={
            "label":"NEGATIVE",
            "score":max (0.75 ,float (response_sales .get ("sentiment",{}).get ("score",0.0 )or 0.0 ))
            }
            response_sales ["emotion_analysis"]={
            "emotion":"neutral",
            "score":float (emotion_score or 0.5 )
            }
            response_signals ["sales"]=response_sales 

    response_payload ={
    "assistant_reply":reply ,
    "actions":actions ,
    "confidence":{
    "reply_confidence":round (reply_confidence ,2 ),
    "decision_confidence":round (decision_confidence ,2 )
    },
    "signals":response_signals ,
    }

    if (
    response_payload ["signals"].get ("underwriting",{}).get ("decision")=="DECLINED"
    and response_payload ["signals"].get ("risk",{}).get ("risk_band")=="HIGH"
    ):
        response_payload ["signals"]["emotion"]={"emotion":"neutral","score":float (emotion_score or 0.5 )}
        if isinstance (response_payload ["signals"].get ("sales"),dict ):
            response_payload ["signals"]["sales"]["sentiment"]={
            "label":"NEGATIVE",
            "score":max (0.75 ,float (response_payload ["signals"]["sales"].get ("sentiment",{}).get ("score",0.0 )or 0.0 ))
            }
            response_payload ["signals"]["sales"]["emotion_analysis"]={
            "emotion":"neutral",
            "score":float (emotion_score or 0.5 )
            }

    return response_payload 
