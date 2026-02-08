"""
SQLite Database Initialization Script
Alternative to MySQL for development/testing
"""

import os 
import sys 
from pathlib import Path 

sys .path .insert (0 ,str (Path (__file__ ).parent .parent ))

from sqlalchemy import create_engine 
from sqlalchemy .orm import sessionmaker 
from database .models import Base 

def init_sqlite_database ():
    """Initialize SQLite database with all tables"""

    db_dir =Path (__file__ ).parent 
    db_file =db_dir /"ey_agentic_ai.db"

    database_url =f"sqlite:///{db_file }"

    print (f"\n{'='*60 }")
    print ("Initializing SQLite Database")
    print (f"{'='*60 }")
    print (f"Database file: {db_file }")

    try :
        engine =create_engine (
        database_url ,
        connect_args ={"check_same_thread":False },
        echo =False 
        )

        print ("\nCreating database tables...")
        Base .metadata .create_all (bind =engine )

        inspector =__import__ ('sqlalchemy').inspect (engine )
        tables =inspector .get_table_names ()

        print (f"✓ Successfully created {len (tables )} tables:\n")

        table_list =[
        "1. users",
        "2. loan_requests",
        "3. eligibility_checks",
        "4. risk_assessments",
        "5. credit_assessments",
        "6. fraud_detections",
        "7. offers",
        "8. intent_detections",
        "9. emotion_analysis",
        "10. persuasion_scores",
        "11. auth_sessions"
        ]

        for table_name in table_list :
            print (f"  ✓ {table_name }")

        print (f"\n{'='*60 }")
        print ("✓ Database Initialization Successful!")
        print (f"{'='*60 }")
        print (f"\nDatabase URL: {database_url }")
        print (f"Location: {db_file }")
        print (f"\nTo use this database, set in .env:")
        print (f"DATABASE_URL=sqlite:///{db_file }")
        print (f"\n{'='*60 }\n")

        return True 

    except Exception as e :
        print (f"\n✗ Error initializing database: {e }\n")
        return False 

if __name__ =="__main__":
    success =init_sqlite_database ()
    sys .exit (0 if success else 1 )
