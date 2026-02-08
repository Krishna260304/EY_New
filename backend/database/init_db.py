import os 
import sys 
from pathlib import Path 

backend_dir =Path (__file__ ).parent .parent 
sys .path .insert (0 ,str (backend_dir .parent ))

from database .models import init_database 

def main ():
    print ("Initializing MySQL Database...")

    try :
        engine =init_database ()
        print ("✓ Database connection established")
        print ("✓ All tables created successfully!")
        print ("\nDatabase URL: "+os .getenv ("DATABASE_URL","mysql+pymysql://root:password@localhost:3306/ey_agentic_ai"))
        print ("\nAvailable tables:")
        print ("  - users")
        print ("  - loan_requests")
        print ("  - eligibility_checks")
        print ("  - risk_assessments")
        print ("  - credit_assessments")
        print ("  - fraud_detections")
        print ("  - offers")
        print ("  - intent_detections")
        print ("  - emotion_analysis")
        print ("  - persuasion_scores")

    except Exception as e :
        print (f"✗ Error initializing database: {str (e )}")
        print ("\nMake sure MySQL is running and accessible at:")
        print ("  Host: localhost")
        print ("  Port: 3306")
        print ("  Username: root")
        print ("  Database: ey_agentic_ai")
        sys .exit (1 )

if __name__ =="__main__":
    main ()
