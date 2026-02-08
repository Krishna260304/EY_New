from typing import Dict ,Optional 
from transformers import pipeline 

_feedback_llm =None 


def _get_feedback_llm ():
    global _feedback_llm 
    if _feedback_llm is None :
        _feedback_llm =pipeline (
        "text2text-generation",
        model ="google/flan-t5-base"
        )
    return _feedback_llm 


def generate_feedback (
verification_result :Dict ,
underwriting_result :Dict ,
risk_result :Dict ,
emotion :Optional [str ]=None 
)->Dict :
    """
    Generates user-friendly feedback explaining the decision.
    Verification failure takes precedence over underwriting approval.
    Adjusts tone based on detected emotion for empathy.
    """

    risk =risk_result .get ("risk_band","MEDIUM")
    uw_decision =underwriting_result .get ("decision","PENDING")
    reasons =risk_result .get ("reasons",[])
    ver_status =(verification_result or {}).get ("status")
    ver_reason =(verification_result or {}).get ("reason")


    tone_prefix =""
    if emotion in ["sadness","fear","concern","worried"]:
        tone_prefix ="Use an empathetic, reassuring tone. "
    elif emotion in ["anger","frustration"]:
        tone_prefix ="Use a calm, understanding tone. "
    elif emotion in ["joy","happy","excited"]:
        tone_prefix ="Use a positive, encouraging tone. "
    else :
        tone_prefix ="Use a professional, clear tone. "


    if ver_status !="verified":
        base_message =(
        "We can't finalize your application yet because document verification didn't pass. "
        f"Reason: {ver_reason or 'Document verification failed'}. "
        "Please update or re-upload the correct required documents (such as a valid Aadhaar format) and we will re-verify promptly."
        )
    elif risk =="HIGH":
        base_message =(
        "The loan application was not approved due to high risk factors. "
        "Key concerns include: "
        +", ".join (reasons or ["policy constraints"])
        +". Our team can discuss alternative options with you if needed."
        )
    else :
        base_message =(
        f"The loan application is {uw_decision .lower ()}. "
        f"Overall risk is {risk .lower ()}."
        )

    prompt =(
    f"{tone_prefix }"
    "Rewrite the following system decision into a polite, clear "
    "message suitable for a loan applicant:\n\n"
    f"{base_message }"
    )

    llm =_get_feedback_llm ()
    response =llm (prompt ,max_new_tokens =120 ,do_sample =False )[0 ]["generated_text"]

    return {
    "feedback":response ,
    "risk":risk ,
    "tone_applied":emotion or "neutral"
    }
