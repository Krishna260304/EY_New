def calculate_credit_score (income :float ,existing_loans :int ,emi :float )->int :
    score =300 
    score +=income *0.01 
    score -=existing_loans *20 
    score -=emi *0.05 
    return max (300 ,min (int (score ),900 ))
