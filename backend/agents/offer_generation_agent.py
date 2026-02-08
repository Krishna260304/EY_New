from typing import Dict ,Any 
from transformers import pipeline 
import torch 
import torch 
from transformers import pipeline 

HF_DEVICE =0 if torch .cuda .is_available ()else -1 

_offer_llm =pipeline (
"text2text-generation",
model ="google/flan-t5-base",
device =HF_DEVICE 
)



def _get_device ():
    return 0 if torch .cuda .is_available ()else -1 


def _get_offer_llm ():
    global _offer_llm 
    if _offer_llm is None :
        _offer_llm =pipeline (
        "text2text-generation",
        model ="google/flan-t5-base",
        device =_get_device (),
        padding =True 
        )
        _offer_llm .model .config .pad_token_id =_offer_llm .model .config .eos_token_id 
        _offer_llm .tokenizer .pad_token_id =_offer_llm .tokenizer .eos_token_id 
    return _offer_llm 


def generate_offer (
application_data :Dict [str ,Any ],
underwriting_result :Dict [str ,Any ],
risk_result :Dict [str ,Any ],
)->Dict [str ,Any ]:

    risk_band =risk_result .get ("risk_band","HIGH")
    income =application_data .get ("monthly_income",0 )

    if risk_band =="HIGH":
        return {
        "offer_available":False ,
        "reason":"High risk profile"
        }

    approved_amount =min (
    application_data .get ("loan_amount",500000 ),
    int (income *20 )
    )
    currency =application_data .get ("currency","INR").upper ()
    currency_symbol ={"INR":"₹","USD":"$","EUR":"€","GBP":"£"}.get (currency ,currency )

    base_rate =10.5 if risk_band =="LOW"else 13.5 
    tenure =60 if risk_band =="LOW"else 36 

    formatted_amount =f"{currency_symbol }{approved_amount :,.0f}"

    prompt =(
    "Generate a short professional loan offer message.\\n"
    f"Loan amount: {formatted_amount }\\n"
    f"Interest rate: {base_rate }%\n"
    f"Tenure: {tenure } months\n"
    "Tone: polite, concise, non-marketing."
    )

    llm =_get_offer_llm ()

    try :
        text =llm (
        prompt ,
        max_new_tokens =60 ,
        num_beams =2 ,
        do_sample =False ,
        pad_token_id =llm .tokenizer .eos_token_id 
        )[0 ]["generated_text"]
    except Exception :
        text ="You are eligible for a loan. Our team will contact you shortly."

    return {
    "offer_available":True ,
    "loan_amount":approved_amount ,
    "interest_rate":base_rate ,
    "tenure_months":tenure ,
    "message":text .strip ()
    }
