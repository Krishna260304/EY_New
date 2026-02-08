from typing import Dict 


def assess_risk (
verification_result :Dict ,
underwriting_result :Dict ,
application_data :Dict 
)->Dict :
    risk_score =0.0 
    reasons =[]

    if verification_result .get ("status")!="verified":
        risk_score +=0.4 
        reasons .append ("Document verification failed")

    uw_risk =underwriting_result .get ("risk","HIGH")
    emi_ratio =float (underwriting_result .get ("emi_ratio",0.0 )or 0.0 )

    if uw_risk =="HIGH":
        risk_score +=0.4 
        reasons .append ("High underwriting risk")
    elif uw_risk =="MEDIUM":
        risk_score +=0.2 
        reasons .append ("Underwriting marked medium risk")


    if emi_ratio >=0.6 :
        risk_score +=0.4 
        reasons .append ("Excessive EMI burden")
    elif emi_ratio >=0.4 :
        risk_score +=0.2 
        reasons .append ("Elevated EMI burden")

    credit_score =application_data .get ("credit_score",0 )
    recent_delinquency =int (application_data .get ("recent_delinquency_months",0 )or 0 )
    urgency_flag =bool (application_data .get ("urgency_flag",False ))
    behavioral =application_data .get ("behavioral_flags",{})or {}
    addr_changes =int (application_data .get ("address_changes_last_12_months",0 )or 0 )
    geo_risk =bool (application_data .get ("geo_risk_flag",False ))
    monthly_income =float (application_data .get ("monthly_income",0 )or 0.0 )
    loan_amount =float (application_data .get ("loan_amount",0 )or 0.0 )
    annual_income =monthly_income *12 if monthly_income else 0.0 
    lti =loan_amount /annual_income if annual_income >0 else 1.0 

    if credit_score <600 :
        risk_score +=0.3 
        reasons .append ("Low credit score")
    elif credit_score <700 :
        risk_score +=0.15 


    if recent_delinquency >=1 :
        risk_score +=0.2 
        reasons .append ("Recent delinquency observed")

    if urgency_flag :
        risk_score +=0.1 
        reasons .append ("High urgency behavior")

    if isinstance (behavioral ,dict ):
        if behavioral .get ("stress_detected"):
            risk_score +=0.1 
            reasons .append ("Stress signals detected")
        if behavioral .get ("inconsistent_statements"):
            risk_score +=0.1 
            reasons .append ("Inconsistent statements detected")

    if addr_changes >=3 :
        risk_score +=0.1 
        reasons .append ("Frequent address changes")

    if geo_risk :
        risk_score +=0.1 
        reasons .append ("Geo-risk flag active")


    if lti >=0.8 :
        risk_score +=0.2 
        reasons .append ("High loan-to-income ratio")
    elif lti >=0.6 :
        risk_score +=0.1 
        reasons .append ("Elevated loan-to-income ratio")

    risk_score =min (round (risk_score ,2 ),1.0 )

    if risk_score >=0.7 :
        risk_band ="HIGH"
    elif risk_score >=0.4 :
        risk_band ="MEDIUM"
    else :
        risk_band ="LOW"

    if risk_band =="LOW"and risk_score ==0.0 :

        risk_score =0.18 

    risk_score_percent =int (round (risk_score *100 ))

    return {
    "risk_band":risk_band ,
    "risk_score":risk_score ,
    "risk_score_percent":risk_score_percent ,
    "reasons":reasons or ["Financial profile appears stable"]
    }
