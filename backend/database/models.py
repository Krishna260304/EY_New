from sqlalchemy import create_engine ,Column ,Integer ,String ,Float ,DateTime ,Text ,Boolean ,ForeignKey ,Table 
from sqlalchemy .ext .declarative import declarative_base 
from sqlalchemy .orm import relationship ,sessionmaker 
from datetime import datetime 
import os 

Base =declarative_base ()

class User (Base ):
    __tablename__ ="users"

    id =Column (Integer ,primary_key =True ,autoincrement =True )
    user_id =Column (String (50 ),unique =True ,nullable =False ,index =True )
    username =Column (String (50 ),unique =True ,nullable =False ,index =True )
    name =Column (String (255 ),nullable =False )
    email =Column (String (255 ),unique =True ,nullable =False ,index =True )
    phone =Column (String (20 ))
    credit_score =Column (Integer )
    annual_income =Column (Float )
    employment_type =Column (String (50 ))
    age =Column (Integer )
    password_hash =Column (String (255 ),nullable =False )
    password_salt =Column (String (255 ),nullable =False )
    is_active =Column (Boolean ,default =True )
    last_login_at =Column (DateTime )
    created_at =Column (DateTime ,default =datetime .utcnow )
    updated_at =Column (DateTime ,default =datetime .utcnow ,onupdate =datetime .utcnow )

    loan_requests =relationship ("LoanRequest",back_populates ="user",cascade ="all, delete-orphan")
    credit_assessments =relationship ("CreditAssessment",back_populates ="user",cascade ="all, delete-orphan")
    fraud_detections =relationship ("FraudDetection",back_populates ="user",cascade ="all, delete-orphan")


class LoanRequest (Base ):
    __tablename__ ="loan_requests"

    id =Column (Integer ,primary_key =True ,autoincrement =True )
    user_id =Column (Integer ,ForeignKey ("users.id"),nullable =False ,index =True )
    loan_amount =Column (Float ,nullable =False )
    loan_term =Column (Integer )
    purpose =Column (String (100 ))
    existing_loans_count =Column (Integer )
    debt_to_income =Column (Float )
    requested_at =Column (DateTime ,default =datetime .utcnow )
    status =Column (String (50 ),default ="pending")
    created_at =Column (DateTime ,default =datetime .utcnow )
    updated_at =Column (DateTime ,default =datetime .utcnow ,onupdate =datetime .utcnow )

    user =relationship ("User",back_populates ="loan_requests")
    eligibility_check =relationship ("EligibilityCheck",uselist =False ,back_populates ="loan_request",cascade ="all, delete-orphan")
    risk_assessment =relationship ("RiskAssessment",uselist =False ,back_populates ="loan_request",cascade ="all, delete-orphan")
    offer =relationship ("Offer",uselist =False ,back_populates ="loan_request",cascade ="all, delete-orphan")


class EligibilityCheck (Base ):
    __tablename__ ="eligibility_checks"

    id =Column (Integer ,primary_key =True ,autoincrement =True )
    loan_request_id =Column (Integer ,ForeignKey ("loan_requests.id"),nullable =False ,index =True )
    eligible =Column (Boolean ,nullable =False )
    confidence =Column (Float )
    reason =Column (Text )
    checked_at =Column (DateTime ,default =datetime .utcnow )

    loan_request =relationship ("LoanRequest",back_populates ="eligibility_check")


class RiskAssessment (Base ):
    __tablename__ ="risk_assessments"

    id =Column (Integer ,primary_key =True ,autoincrement =True )
    loan_request_id =Column (Integer ,ForeignKey ("loan_requests.id"),nullable =False ,index =True )
    risk_tier =Column (String (50 ),nullable =False )
    risk_score =Column (Float )
    confidence =Column (Float )
    delinquency_12m =Column (Integer )
    outstanding_debt =Column (Float )
    num_hard_inquiries =Column (Integer )
    assessed_at =Column (DateTime ,default =datetime .utcnow )

    loan_request =relationship ("LoanRequest",back_populates ="risk_assessment")


class CreditAssessment (Base ):
    __tablename__ ="credit_assessments"

    id =Column (Integer ,primary_key =True ,autoincrement =True )
    user_id =Column (Integer ,ForeignKey ("users.id"),nullable =False ,index =True )
    credit_score =Column (Integer )
    previous_score =Column (Integer )
    score_change =Column (Integer )
    assessment_date =Column (DateTime ,default =datetime .utcnow )
    details =Column (Text )

    user =relationship ("User",back_populates ="credit_assessments")


class FraudDetection (Base ):
    __tablename__ ="fraud_detections"

    id =Column (Integer ,primary_key =True ,autoincrement =True )
    user_id =Column (Integer ,ForeignKey ("users.id"),nullable =False ,index =True )
    fraud_probability =Column (Float )
    status =Column (String (50 ))
    detected_at =Column (DateTime ,default =datetime .utcnow )
    details =Column (Text )

    user =relationship ("User",back_populates ="fraud_detections")


class Offer (Base ):
    __tablename__ ="offers"

    id =Column (Integer ,primary_key =True ,autoincrement =True )
    loan_request_id =Column (Integer ,ForeignKey ("loan_requests.id"),nullable =False ,index =True )
    recommended_rate =Column (Float )
    recommended_tenure =Column (Integer )
    max_amount =Column (Float )
    interest_type =Column (String (50 ))
    offer_expires_at =Column (DateTime )
    created_at =Column (DateTime ,default =datetime .utcnow )
    updated_at =Column (DateTime ,default =datetime .utcnow ,onupdate =datetime .utcnow )

    loan_request =relationship ("LoanRequest",back_populates ="offer")


class IntentDetection (Base ):
    __tablename__ ="intent_detections"

    id =Column (Integer ,primary_key =True ,autoincrement =True )
    user_id =Column (String (50 ),nullable =False ,index =True )
    message =Column (Text )
    detected_intent =Column (String (100 ))
    intent_confidence =Column (Float )
    detected_at =Column (DateTime ,default =datetime .utcnow )


class EmotionAnalysis (Base ):
    __tablename__ ="emotion_analysis"

    id =Column (Integer ,primary_key =True ,autoincrement =True )
    user_id =Column (String (50 ),nullable =False ,index =True )
    message =Column (Text )
    detected_emotion =Column (String (50 ))
    emotion_score =Column (Float )
    analyzed_at =Column (DateTime ,default =datetime .utcnow )


class PersuasionScore (Base ):
    __tablename__ ="persuasion_scores"

    id =Column (Integer ,primary_key =True ,autoincrement =True )
    user_id =Column (String (50 ),nullable =False ,index =True )
    intent_confidence =Column (Float )
    sentiment_score =Column (Float )
    urgency =Column (Integer )
    hesitation =Column (Integer )
    message_length =Column (Integer )
    conversion_bucket =Column (String (50 ))
    calculated_at =Column (DateTime ,default =datetime .utcnow )


class AuthSession (Base ):
    __tablename__ ="auth_sessions"

    id =Column (Integer ,primary_key =True ,autoincrement =True )
    user_id =Column (Integer ,ForeignKey ("users.id"),nullable =False ,index =True )
    token =Column (String (255 ),unique =True ,nullable =False ,index =True )
    created_at =Column (DateTime ,default =datetime .utcnow )
    expires_at =Column (DateTime ,nullable =True )
    active =Column (Boolean ,default =True )


def create_database_connection ():
    db_url =os .getenv (
    "DATABASE_URL",
    "mysql+pymysql://root:password@localhost:3306/ey_agentic_ai"
    )
    engine =create_engine (db_url ,echo =False )
    return engine 


def init_database ():
    engine =create_database_connection ()
    Base .metadata .create_all (engine )
    return engine 


def get_session ():
    engine =create_database_connection ()
    SessionLocal =sessionmaker (bind =engine )
    return SessionLocal ()


if __name__ =="__main__":
    init_database ()
    print ("Database tables created successfully!")
