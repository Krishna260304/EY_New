from fastapi import APIRouter 
from pydantic import BaseModel 
from transformers import pipeline 
from typing import Dict ,Any ,Union ,Optional 

from ml .infer_intent import predict_intent 
from ml .infer_emotion import analyze_emotion 
from ml .gpu_accelerated_inference import accelerator 

import torch 
from transformers import pipeline 

HF_DEVICE =0 if torch .cuda .is_available ()else -1 


router =APIRouter (prefix ="/agent/sales",tags =["Sales & Persuasion"])


_sentiment_analyzer :Optional [Any ]=None 

def get_sentiment_analyzer ():
    global _sentiment_analyzer 
    if _sentiment_analyzer is None :
        try :
            _sentiment_analyzer =pipeline (
            "sentiment-analysis",
            model ="distilbert-base-uncased-finetuned-sst-2-english",
            device =HF_DEVICE ,
            )
        except Exception as e :
            print (f"Warning: Could not load sentiment analyzer: {e }")
            _sentiment_analyzer ="unavailable"
    return _sentiment_analyzer if _sentiment_analyzer !="unavailable"else None 


class SalesAnalyzeRequest (BaseModel ):
    message :str 


def compute_urgency (text :str )->int :
    t =text .lower ()
    score =0 
    for w in ["urgent","immediately","asap","right now","emergency","today"]:
        if w in t :
            score +=25 
    score +=t .count ("!")*10 
    return min (score ,100 )


def compute_hesitation (text :str )->int :
    t =text .lower ()
    score =0 
    for w in ["maybe","not sure","confused","doubt","unsure","thinking"]:
        if w in t :
            score +=20 
    score +=t .count ("?")*5 
    return min (score ,100 )


def compute_persuasion_index (
sentiment_label :str ,
intent_conf :float ,
urgency :int ,
hesitation :int ,
)->int :
    base =50 
    if sentiment_label =="POSITIVE":
        base +=10 
    elif sentiment_label =="NEGATIVE":
        base -=10 

    base +=(intent_conf -0.5 )*40 
    base +=(urgency -50 )*0.2 
    base -=(hesitation -50 )*0.2 

    return int (max (0 ,min (100 ,base )))


@router .post ("/analyze")
async def analyze_message (
payload :Union [SalesAnalyzeRequest ,Dict [str ,Any ]]
)->Dict [str ,Any ]:
    if isinstance (payload ,SalesAnalyzeRequest ):
        text =payload .message or ""
    elif isinstance (payload ,dict ):
        text =str (payload .get ("message")or payload .get ("text")or "")
    else :
        text =""

    text =text .strip ()

    if not text :
        return {
        "intent":None ,
        "intent_confidence":0.0 ,
        "sentiment":{"label":"NEUTRAL","score":0.0 },
        "urgency":0 ,
        "hesitation":0 ,
        "persuasion_index":0 ,
        "tone_summary":"neutral",
        "emotion_analysis":{"emotion":None ,"score":0.0 },
        }

    try :
        intent_result =predict_intent (text )
    except Exception :
        intent_result =None 

    intent =None 
    intent_conf =0.0 

    if isinstance (intent_result ,dict ):
        intent =intent_result .get ("intent")
        intent_conf =float (intent_result .get ("confidence")or 0.0 )
    elif isinstance (intent_result ,list )and intent_result :
        first =intent_result [0 ]
        if isinstance (first ,dict ):
            intent =first .get ("intent")or first .get ("label")
            intent_conf =float (first .get ("confidence")or first .get ("score")or 0.0 )

    sentiment_label ="NEUTRAL"
    sentiment_score =0.0 

    try :
        analyzer =get_sentiment_analyzer ()
        if analyzer :

            s_out =accelerator .predict_transformer_model (analyzer ,text ,use_npu =False )
            if isinstance (s_out ,list )and s_out :
                s =s_out [0 ]
                if isinstance (s ,dict ):
                    sentiment_label =str (s .get ("label")or "NEUTRAL").upper ()
                    sentiment_score =float (s .get ("score")or 0.0 )
            elif isinstance (s_out ,dict ):
                sentiment_label =str (s_out .get ("label")or "NEUTRAL").upper ()
                sentiment_score =float (s_out .get ("score")or 0.0 )
    except Exception as e :
        print (f"Sentiment analysis failed: {e }")

    urgency_raw =compute_urgency (text )
    urgency =round (urgency_raw /100.0 ,2 )
    hesitation =compute_hesitation (text )
    persuasion =compute_persuasion_index (
    sentiment_label =sentiment_label ,
    intent_conf =intent_conf ,
    urgency =urgency ,
    hesitation =hesitation ,
    )

    if persuasion >70 :
        tone ="highly convertible"
    elif persuasion <40 :
        tone ="low-conversion"
    else :
        tone ="concerned but convertible"

    try :
        emotion_out =analyze_emotion (text )
    except Exception :
        emotion_out =None 

    emotion =None 
    emotion_score =0.0 

    if isinstance (emotion_out ,dict ):
        emotion =emotion_out .get ("emotion")or emotion_out .get ("label")
        emotion_score =float (emotion_out .get ("score")or 0.0 )
    elif isinstance (emotion_out ,list )and emotion_out :
        first =emotion_out [0 ]
        if isinstance (first ,dict ):
            emotion =first .get ("emotion")or first .get ("label")
            emotion_score =float (first .get ("score")or 0.0 )
        elif isinstance (first ,list ):
            best =max (
            [d for d in first if isinstance (d ,dict )],
            key =lambda d :float (d .get ("score")or 0.0 ),
            default =None ,
            )
            if best :
                emotion =best .get ("emotion")or best .get ("label")
                emotion_score =float (best .get ("score")or 0.0 )


    if sentiment_score ==0.0 and emotion_score >0.0 :
        sentiment_score =emotion_score 
        if emotion :
            sentiment_label =str (emotion ).upper ()

    return {
    "intent":intent ,
    "intent_confidence":intent_conf ,
    "sentiment":{
    "label":sentiment_label ,
    "score":sentiment_score ,
    },
    "urgency":urgency ,
    "urgency_raw":urgency_raw ,
    "hesitation":hesitation ,
    "persuasion_index":persuasion ,
    "tone_summary":tone ,
    "emotion_analysis":{
    "emotion":emotion ,
    "score":emotion_score ,
    },
    }
