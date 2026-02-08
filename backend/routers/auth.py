from fastapi import APIRouter ,HTTPException ,Depends ,Header 
from pydantic import BaseModel ,EmailStr 
from typing import Optional 
from datetime import datetime ,timedelta 
import secrets 

from database .models import get_session ,User ,AuthSession 
from utils .auth_utils import create_password ,verify_password 

router =APIRouter (prefix ="/auth",tags =["Auth"])

class RegisterRequest (BaseModel ):
    username :str 
    name :str 
    email :EmailStr 
    phone :Optional [str ]=None 
    password :str 

class RegisterResponse (BaseModel ):
    user_id :int 
    username :str 
    email :EmailStr 
    created_at :datetime 

class LoginRequest (BaseModel ):
    username_or_email :str 
    password :str 

class LoginResponse (BaseModel ):
    token :str 
    expires_at :Optional [datetime ]

class MeResponse (BaseModel ):
    id :int 
    username :str 
    name :str 
    email :EmailStr 
    phone :Optional [str ]
    is_active :bool 
    created_at :datetime 
    last_login_at :Optional [datetime ]


def get_db ():
    db =get_session ()
    try :
        yield db 
    finally :
        db .close ()


def _find_user (db ,username_or_email :str )->Optional [User ]:
    u =db .query (User ).filter (User .username ==username_or_email ).first ()
    if not u :
        u =db .query (User ).filter (User .email ==username_or_email ).first ()
    return u 


@router .post ("/register",response_model =RegisterResponse )
def register (data :RegisterRequest ,db =Depends (get_db )):
    if db .query (User ).filter (User .username ==data .username ).first ():
        raise HTTPException (status_code =409 ,detail ="Username already exists")
    if db .query (User ).filter (User .email ==data .email ).first ():
        raise HTTPException (status_code =409 ,detail ="Email already exists")

    pwd_hash ,salt =create_password (data .password )
    user =User (
    user_id =f"U-{secrets .token_hex (6 )}",
    username =data .username ,
    name =data .name ,
    email =str (data .email ),
    phone =data .phone ,
    password_hash =pwd_hash ,
    password_salt =salt ,
    is_active =True ,
    created_at =datetime .utcnow (),
    updated_at =datetime .utcnow (),
    )
    db .add (user )
    db .commit ()
    db .refresh (user )

    return RegisterResponse (
    user_id =user .id ,
    username =user .username ,
    email =user .email ,
    created_at =user .created_at ,
    )


@router .post ("/login",response_model =LoginResponse )
def login (data :LoginRequest ,db =Depends (get_db )):
    user =_find_user (db ,data .username_or_email )
    if not user or not user .is_active :
        raise HTTPException (status_code =401 ,detail ="Invalid credentials or inactive user")
    if not verify_password (data .password ,user .password_salt ,user .password_hash ):
        raise HTTPException (status_code =401 ,detail ="Invalid credentials")

    token =secrets .token_urlsafe (32 )
    expires =datetime .utcnow ()+timedelta (hours =12 )

    sess =AuthSession (user_id =user .id ,token =token ,created_at =datetime .utcnow (),expires_at =expires ,active =True )
    db .add (sess )
    user .last_login_at =datetime .utcnow ()
    db .commit ()

    return LoginResponse (token =token ,expires_at =expires )


@router .post ("/logout")
def logout (authorization :Optional [str ]=Header (None ),db =Depends (get_db )):
    if not authorization or not authorization .lower ().startswith ("bearer "):
        raise HTTPException (status_code =400 ,detail ="Missing Bearer token")
    token =authorization .split ()[1 ]
    sess =db .query (AuthSession ).filter (AuthSession .token ==token ,AuthSession .active ==True ).first ()
    if not sess :
        raise HTTPException (status_code =404 ,detail ="Session not found")
    sess .active =False 
    db .commit ()
    return {"ok":True }


@router .get ("/me",response_model =MeResponse )
def me (authorization :Optional [str ]=Header (None ),db =Depends (get_db )):
    if not authorization or not authorization .lower ().startswith ("bearer "):
        raise HTTPException (status_code =401 ,detail ="Unauthorized")
    token =authorization .split ()[1 ]
    sess =db .query (AuthSession ).filter (AuthSession .token ==token ,AuthSession .active ==True ).first ()
    if not sess or (sess .expires_at and sess .expires_at <datetime .utcnow ()):
        raise HTTPException (status_code =401 ,detail ="Session expired or invalid")
    user =db .query (User ).filter (User .id ==sess .user_id ).first ()
    if not user :
        raise HTTPException (status_code =404 ,detail ="User not found")
    return MeResponse (
    id =user .id ,
    username =user .username ,
    name =user .name ,
    email =user .email ,
    phone =user .phone ,
    is_active =user .is_active ,
    created_at =user .created_at ,
    last_login_at =user .last_login_at ,
    )
