import secrets 
import hashlib 
from typing import Tuple 

PBKDF2_ITERATIONS =200_000 


def make_salt ()->str :
    return secrets .token_hex (16 )


def hash_password (password :str ,salt :str )->str :
    dk =hashlib .pbkdf2_hmac (
    "sha256",
    password .encode ("utf-8"),
    salt .encode ("utf-8"),
    PBKDF2_ITERATIONS ,
    )
    return dk .hex ()


def create_password (password :str )->Tuple [str ,str ]:
    salt =make_salt ()
    return hash_password (password ,salt ),salt 


def verify_password (password :str ,salt :str ,expected_hash :str )->bool :
    return hash_password (password ,salt )==expected_hash 
