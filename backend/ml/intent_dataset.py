import pandas as pd 
import torch 
from torch .utils .data import Dataset 


class IntentDataset (Dataset ):
    def __init__ (self ,csv_path ,tokenizer ,label2id ,max_length =64 ):
        self .df =pd .read_csv (csv_path )
        self .tokenizer =tokenizer 
        self .label2id =label2id 
        self .max_length =max_length 

    def __len__ (self ):
        return len (self .df )

    def __getitem__ (self ,idx ):
        row =self .df .iloc [idx ]
        text =row ["text"]
        label =self .label2id [row ["intent"]]

        encoding =self .tokenizer (
        text ,
        truncation =True ,
        padding ="max_length",
        max_length =self .max_length ,
        return_tensors ="pt",
        )

        return {
        "input_ids":encoding ["input_ids"].squeeze (0 ),
        "attention_mask":encoding ["attention_mask"].squeeze (0 ),
        "labels":torch .tensor (label ,dtype =torch .long ),
        }
