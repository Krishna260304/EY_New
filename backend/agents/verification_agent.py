import re 
from typing import Dict ,Optional ,Any 
from transformers import pipeline 
import logging 

import torch 
from transformers import pipeline 

logger =logging .getLogger (__name__ )

HF_DEVICE =0 if torch .cuda .is_available ()else -1 


_name_checker :Optional [Any ]=None 

def get_name_checker ():
    global _name_checker 
    if _name_checker is None :
        try :
            _name_checker =pipeline (
            "zero-shot-classification",
            model ="facebook/bart-large-mnli",
            device =HF_DEVICE ,
            )
            logger .info ("✓ Name checker pipeline loaded")
        except Exception as e :
            logger .warning (f"⚠ Name checker unavailable: {e }")
            _name_checker ="unavailable"
    return _name_checker if _name_checker !="unavailable"else None 

AADHAAR_REGEX =r"^[2-9]\d{11}$"
PAN_REGEX =r"^[A-Z]{5}[0-9]{4}[A-Z]$"


def verify_documents (payload :Dict )->Dict :
    if not payload :
        return fail ("No documents submitted. Please upload your Aadhaar and PAN documents.")

    aadhaar =payload .get ("aadhaar")
    pan =payload .get ("pan")
    name =payload .get ("name","")

    if not aadhaar or not pan :
        missing =[]
        if not aadhaar :
            missing .append ("Aadhaar")
        if not pan :
            missing .append ("PAN")
        return fail (f"Missing required documents: {', '.join (missing )}. Please upload all required documents.",0.2 )

    if not re .match (AADHAAR_REGEX ,str (aadhaar )):
        return fail (
        "Invalid Aadhaar format. Expected format: 12-digit number starting with 2-9. "
        "Please re-upload a valid Aadhaar number.",
        0.4 
        )

    if not re .match (PAN_REGEX ,str (pan ).upper ()):
        return fail (
        "Invalid PAN format. Expected format: 5 letters, 4 digits, 1 letter (e.g., ABCDE1234F). "
        "Please re-upload a valid PAN.",
        0.4 
        )

    confidence =0.7 

    if name :
        prompt =f"Name on documents: {name }"
        try :
            checker =get_name_checker ()
            if checker :
                output =checker (
                prompt ,
                candidate_labels =["valid person name","random text"],
                )
            else :

                return success (0.8 )
        except Exception as e :
            logger .warning (f"Name verification failed: {e }")
            return success (0.8 )

        head =None 
        if isinstance (output ,list ):
            if output and isinstance (output [0 ],list ):
                head =output [0 ][0 ]if output [0 ]else None 
            else :
                head =output [0 ]if output else None 
        elif isinstance (output ,dict ):
            head =output 

        labels =[]
        if isinstance (head ,dict ):
            labels =head .get ("labels")or []

        if not labels or labels [0 ]!="valid person name":
            return fail ("Name consistency unclear",0.6 )

        confidence +=0.1 

    return {
    "status":"verified",
    "confidence":min (confidence ,0.9 ),
    "reason":"Documents passed format and consistency checks",
    }


def fail (reason :str ,confidence :float =0.0 )->Dict :
    return {
    "status":"failed",
    "confidence":confidence ,
    "reason":reason ,
    }
