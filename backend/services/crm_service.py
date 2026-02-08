def get_user_details (user_id :str ,fake_users :dict ):
    return fake_users .get (user_id ,{"error":"User not found"})
