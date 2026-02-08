from typing import Dict 


EMI_THRESHOLD_AUTO_REVIEW =0.40 
EMI_THRESHOLD_AUTO_REJECT =0.60 


def underwrite_application (application_data :Dict )->Dict :
    income =application_data .get ("monthly_income",0 )
    existing_emi =application_data .get ("existing_emi",0 )
    credit_score =application_data .get ("credit_score",0 )
    employment_years =application_data .get ("employment_years",0 )
    business_vintage =int (application_data .get ("business_vintage_years",0 )or 0 )
    itr_years =int (application_data .get ("itr_years_submitted",0 )or 0 )
    bank_stmt_months =int (application_data .get ("bank_statement_months",0 )or 0 )

    emi_ratio =existing_emi /income if income >0 else 1.0 
    lti =application_data .get ("loan_amount",0 )/(income *12 )if income >0 else 1.0 

    reasons =[]
    decision ="APPROVED"
    risk ="LOW"


    if emi_ratio >EMI_THRESHOLD_AUTO_REJECT :
        decision ="DECLINED"
        risk ="HIGH"
        reasons .append (f"Excessive EMI burden (EMI ratio: {emi_ratio :.1%} exceeds {EMI_THRESHOLD_AUTO_REJECT :.0%} threshold)")
    elif emi_ratio >EMI_THRESHOLD_AUTO_REVIEW :
        decision ="REVIEW"
        risk ="MEDIUM"
        reasons .append (f"Elevated EMI burden (EMI ratio: {emi_ratio :.1%} exceeds {EMI_THRESHOLD_AUTO_REVIEW :.0%} threshold)")


    if credit_score <600 :
        decision ="DECLINED"
        risk ="HIGH"
        reasons .append ("Very low credit score")
    elif credit_score <700 and decision !="DECLINED":
        if decision =="APPROVED":
            decision ="REVIEW"
            risk ="MEDIUM"
        reasons .append ("Moderate credit score")


    if employment_years <1 and decision !="DECLINED":
        if decision =="APPROVED":
            decision ="REVIEW"
            risk ="MEDIUM"
        reasons .append ("Insufficient employment history")
    elif business_vintage <2 or itr_years <1 or bank_stmt_months <6 :
        if decision =="APPROVED":
            decision ="REVIEW"
            risk ="MEDIUM"
        if business_vintage <2 :
            reasons .append ("New business (less than 2 years)")
        if itr_years <1 :
            reasons .append ("No ITR filed")
        if bank_stmt_months <6 :
            reasons .append ("Insufficient banking history")


    if lti >0.5 and decision =="APPROVED":
        decision ="REVIEW"
        risk ="MEDIUM"
        reasons .append ("Elevated loan-to-income ratio")


    if decision =="APPROVED"and not reasons :
        reasons .append ("Good financial profile")

    return {
    "decision":decision ,
    "risk":risk ,
    "emi_ratio":round (emi_ratio ,2 ),
    "credit_score":credit_score ,
    "reasons":reasons 
    }
