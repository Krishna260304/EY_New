from fastapi import APIRouter 

router =APIRouter (prefix ="/crm",tags =["CRM"])

fake_users ={
"1001":{
"name":"R****h K****r",
"dob":"1998-06-12",
"phone":"98*****210",
"address":"Mumbai, MH"
},
"1002":{
"name":"P****a M****l",
"dob":"1995-11-22",
"phone":"90*****876",
"address":"Delhi, DL"
}
}

@router .get ("/user/{user_id}")
def get_user (user_id :str ):
    return fake_users .get (user_id ,{"error":"User not found"})
