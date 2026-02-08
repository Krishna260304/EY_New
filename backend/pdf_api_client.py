"""
PDF Report Generator - API Client Utility
Provides convenient functions to generate PDF reports via HTTP requests
"""

import requests 
import json 
import os 
from pathlib import Path 
from datetime import datetime 
from typing import Dict ,Any ,Optional 


class PDFReportClient :
    """Client for PDF Report API endpoints"""

    def __init__ (self ,base_url :str ="http://localhost:8000"):
        """
        Initialize PDF Report Client
        
        Args:
            base_url: Base URL of the FastAPI server (default: http://localhost:8000)
        """
        self .base_url =base_url 
        self .pdf_endpoint =f"{base_url }/pdf-reports"

    def generate_application_pdf (
    self ,
    application_data :Dict [str ,Any ],
    output_file :Optional [str ]=None ,
    save_to_server :bool =False 
    )->Dict [str ,Any ]:
        """
        Generate a PDF report for a loan application approval
        
        Args:
            application_data: Dictionary containing application details
            output_file: Optional local file path to save PDF
            save_to_server: If True, saves PDF on server instead of downloading
        
        Returns:
            Dictionary with status and file information
        """
        try :
            payload ={
            "application_data":application_data ,
            "save_to_file":save_to_server ,
            "filepath":None 
            }

            response =requests .post (
            f"{self .pdf_endpoint }/application-approval-pdf",
            json =payload ,
            timeout =30 
            )

            if response .status_code ==200 :
                if output_file :

                    with open (output_file ,'wb')as f :
                        f .write (response .content )
                    return {
                    "status":"success",
                    "message":"PDF generated and saved",
                    "file":output_file ,
                    "size":len (response .content )
                    }
                else :
                    return {
                    "status":"success",
                    "message":"PDF generated",
                    "content":response .content ,
                    "size":len (response .content )
                    }
            else :
                return {
                "status":"error",
                "message":f"Server error: {response .status_code }",
                "details":response .text 
                }

        except Exception as e :
            return {
            "status":"error",
            "message":"Failed to generate PDF",
            "error":str (e )
            }

    def generate_statistics_pdf (
    self ,
    statistics_data :Dict [str ,Any ],
    output_file :Optional [str ]=None ,
    save_to_server :bool =False 
    )->Dict [str ,Any ]:
        """
        Generate a PDF report with statistics
        
        Args:
            statistics_data: Dictionary containing statistics
            output_file: Optional local file path to save PDF
            save_to_server: If True, saves PDF on server
        
        Returns:
            Dictionary with status and file information
        """
        try :
            payload ={
            "statistics_data":statistics_data ,
            "save_to_file":save_to_server ,
            "filepath":None 
            }

            response =requests .post (
            f"{self .pdf_endpoint }/statistics-pdf",
            json =payload ,
            timeout =30 
            )

            if response .status_code ==200 :
                if output_file :
                    with open (output_file ,'wb')as f :
                        f .write (response .content )
                    return {
                    "status":"success",
                    "message":"Statistics PDF generated and saved",
                    "file":output_file ,
                    "size":len (response .content )
                    }
                else :
                    return {
                    "status":"success",
                    "message":"Statistics PDF generated",
                    "content":response .content ,
                    "size":len (response .content )
                    }
            else :
                return {
                "status":"error",
                "message":f"Server error: {response .status_code }",
                "details":response .text 
                }

        except Exception as e :
            return {
            "status":"error",
            "message":"Failed to generate statistics PDF",
            "error":str (e )
            }

    def get_sample_application_pdf (self ,output_file :str ="sample_application.pdf")->Dict [str ,Any ]:
        """
        Download sample application PDF
        
        Args:
            output_file: Local file path to save PDF
        
        Returns:
            Dictionary with status information
        """
        try :
            response =requests .get (f"{self .pdf_endpoint }/sample-application-pdf",timeout =30 )

            if response .status_code ==200 :
                with open (output_file ,'wb')as f :
                    f .write (response .content )
                return {
                "status":"success",
                "message":"Sample application PDF downloaded",
                "file":output_file ,
                "size":len (response .content )
                }
            else :
                return {
                "status":"error",
                "message":f"Failed to download: {response .status_code }"
                }

        except Exception as e :
            return {
            "status":"error",
            "message":"Failed to download sample PDF",
            "error":str (e )
            }

    def get_sample_statistics_pdf (self ,output_file :str ="sample_statistics.pdf")->Dict [str ,Any ]:
        """
        Download sample statistics PDF
        
        Args:
            output_file: Local file path to save PDF
        
        Returns:
            Dictionary with status information
        """
        try :
            response =requests .get (f"{self .pdf_endpoint }/sample-statistics-pdf",timeout =30 )

            if response .status_code ==200 :
                with open (output_file ,'wb')as f :
                    f .write (response .content )
                return {
                "status":"success",
                "message":"Sample statistics PDF downloaded",
                "file":output_file ,
                "size":len (response .content )
                }
            else :
                return {
                "status":"error",
                "message":f"Failed to download: {response .status_code }"
                }

        except Exception as e :
            return {
            "status":"error",
            "message":"Failed to download sample PDF",
            "error":str (e )
            }

    def check_health (self )->Dict [str ,Any ]:
        """
        Check PDF Report service health
        
        Returns:
            Service health status
        """
        try :
            response =requests .get (f"{self .pdf_endpoint }/health",timeout =10 )
            return response .json ()

        except Exception as e :
            return {
            "status":"error",
            "message":"Failed to reach service",
            "error":str (e )
            }



def download_sample_reports (output_dir :str ="./reports"):
    """Download sample PDFs for testing"""
    """
    Download sample PDFs for testing
    
    Args:
        output_dir: Directory to save reports
    """

    Path (output_dir ).mkdir (parents =True ,exist_ok =True )

    client =PDFReportClient ()

    print (f"Downloading sample reports to {output_dir }...")


    app_result =client .get_sample_application_pdf (f"{output_dir }/sample_application.pdf")
    print (f"Application PDF: {app_result ['message']}")


    stats_result =client .get_sample_statistics_pdf (f"{output_dir }/sample_statistics.pdf")
    print (f"Statistics PDF: {stats_result ['message']}")

    return {
    "application":app_result ,
    "statistics":stats_result 
    }


def generate_application_report (
customer_name :str ,
customer_id :str ,
loan_amount :float ,
credit_score :int ,
status :str ="APPROVED",
output_dir :str ="./reports"
)->Dict [str ,Any ]:
    """
    Generate a custom application report
    
    Args:
        customer_name: Customer name
        customer_id: Customer ID
        loan_amount: Loan amount
        credit_score: Credit score
        status: Approval status (APPROVED/DECLINED)
        output_dir: Directory to save report
    
    Returns:
        Generation result
    """

    Path (output_dir ).mkdir (parents =True ,exist_ok =True )


    application_data ={
    "customer":{
    "name":customer_name ,
    "id":customer_id ,
    "email":f"{customer_name .lower ().replace (' ','.')}@example.com",
    "phone":"+91-98765-43210",
    "age":35 ,
    "employment_type":"Salaried",
    "monthly_income":50000 ,
    "annual_income":600000 ,
    "credit_score":credit_score 
    },
    "application":{
    "id":f"APP-{datetime .now ().strftime ('%Y%m%d%H%M%S')}",
    "loan_amount":loan_amount ,
    "application_date":datetime .now ().strftime ("%Y-%m-%d"),
    "loan_term":60 ,
    "purpose":"Personal",
    "existing_loans_count":1 ,
    "debt_to_income":0.30 
    },
    "verification":{
    "id_status":"Verified",
    "income_status":"Verified",
    "address_status":"Verified",
    "employment_status":"Verified",
    "document_status":"Verified"
    },
    "underwriting":{
    "decision":status ,
    "emi_ratio":0.35 ,
    "decision_confidence":0.92 if status =="APPROVED"else 0.75 ,
    "processing_status":"Completed",
    "comments":f"Application {status .lower ()}"
    },
    "risk":{
    "risk_band":"LOW"if status =="APPROVED"else "HIGH",
    "risk_score":0.15 if status =="APPROVED"else 0.75 ,
    "confidence":0.88 ,
    "repayment_risk":"Low"if status =="APPROVED"else "High",
    "fraud_risk":"Low",
    "delinquency_12m":0 ,
    "outstanding_debt":150000 ,
    "num_hard_inquiries":2 
    },
    "offer":{
    "approved_amount":loan_amount if status =="APPROVED"else 0 ,
    "interest_rate":8.5 ,
    "tenure":60 ,
    "emi":(loan_amount /60 *1.085 )if status =="APPROVED"else 0 ,
    "processing_fee":5000 ,
    "total_payable":(loan_amount *1.085 +5000 )if status =="APPROVED"else 0 ,
    "offer_validity":"Valid till 2025-03-08"
    },
    "feedback":{
    "assistant_reply":f"Congratulations! Your loan application has been {status .lower ()}.",
    "actions":["send_approval_email","schedule_document_collection"],
    "next_steps":"Please visit our branch with required documents."
    }
    }

    client =PDFReportClient ()
    output_file =f"{output_dir }/application_{customer_id }_{datetime .now ().strftime ('%Y%m%d_%H%M%S')}.pdf"

    result =client .generate_application_pdf (application_data ,output_file )

    return result 


if __name__ =="__main__":
    print ("="*60 )
    print ("PDF Report Generator - API Client")
    print ("="*60 )


    client =PDFReportClient ()
    print ("\nChecking service health...")
    health =client .check_health ()
    print (f"Status: {health .get ('status','Unknown')}")
    print (f"Service: {health .get ('service','Unknown')}")


    print ("\n"+"="*60 )
    print ("Downloading sample reports...")
    print ("="*60 )
    results =download_sample_reports ("./reports")


    print ("\n"+"="*60 )
    print ("Generating custom application report...")
    print ("="*60 )
    report =generate_application_report (
    customer_name ="John Doe",
    customer_id ="CUST-2025-001",
    loan_amount =500000 ,
    credit_score =720 ,
    status ="APPROVED"
    )
    print (f"Custom Report: {report ['message']}")
    if report ['status']=='success':
        print (f"File: {report .get ('file','N/A')}")

    print ("\n"+"="*60 )
    print ("✓ All operations completed!")
    print ("="*60 )
