from transformers import pipeline 
import torch 
from utils .gpu_utils import setup_gpu_environment ,get_device_manager 


setup_gpu_environment ()
device_manager =get_device_manager ()

_analyzer =None 


def _load ():
    global _analyzer 
    if _analyzer is None :
        device_str ="cuda"if torch .cuda .is_available ()else "cpu"
        _analyzer =pipeline (
        "text-classification",
        model ="j-hartmann/emotion-english-distilroberta-base",
        top_k =None ,
        device =device_str ,
        )
    return _analyzer 


def _normalize (output ):
    """Return a single dict with emotion + score regardless of pipeline shape."""
    best =None 

    if isinstance (output ,dict ):
        label =output .get ("emotion")or output .get ("label")
        score =float (output .get ("score")or 0.0 )
        best ={"emotion":label ,"score":score }

    elif isinstance (output ,list )and output :
        first =output [0 ]

        if isinstance (first ,list ):
            candidates =[d for d in first if isinstance (d ,dict )]
            if candidates :
                best =max (candidates ,key =lambda d :float (d .get ("score")or 0.0 ))

        elif isinstance (first ,dict ):
            best =first 

    if isinstance (best ,dict ):
        label =best .get ("emotion")or best .get ("label")
        score =float (best .get ("score")or 0.0 )
        return {"emotion":label ,"score":score }


    return {"emotion":None ,"score":0.0 }


def analyze_emotion (text ):
    raw =_load ()(text )
    return _normalize (raw )
