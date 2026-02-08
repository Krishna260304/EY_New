"""
PDF Report Router
API endpoints for generating PDF reports for loan approvals and statistics
"""

from fastapi import APIRouter ,HTTPException ,Response 
from fastapi .responses import FileResponse ,StreamingResponse 
from typing import Dict ,Any ,Optional 
import io 
import os 
from datetime import datetime 

from utils .pdf_generator import PDFReportGenerator ,generate_application_pdf ,generate_statistics_pdf 

router =APIRouter (prefix ="/pdf-reports",tags =["PDF Reports"])


@router .post ("/application-approval-pdf")
async def generate_application_approval_pdf (
application_data :Dict [str ,Any ],
save_to_file :bool =False ,
filepath :Optional [str ]=None 
)->Response :
    """
    Generate a PDF report for a single loan application approval
    
    Args:
        application_data: Dictionary containing:
            - customer: {name, id, monthly_income, credit_score}
            - application: {loan_amount, application_date}
            - verification: {id_status, income_status, address_status, ...}
            - underwriting: {decision, emi_ratio, decision_confidence, ...}
            - risk: {risk_band, risk_score, repayment_risk, fraud_risk, ...}
            - offer: {approved_amount, interest_rate, tenure, emi, ...} (if approved)
            - feedback: {assistant_reply, actions, ...}
        save_to_file: Whether to save PDF to disk (default: False)
        filepath: Path to save PDF if save_to_file is True
    
    Returns:
        PDF file as StreamingResponse or saved file response
    """
    try :

        if not application_data .get ('customer'):
            raise HTTPException (status_code =400 ,detail ="Missing customer data")
        if not application_data .get ('application'):
            raise HTTPException (status_code =400 ,detail ="Missing application data")


        generator =PDFReportGenerator ()

        if save_to_file :
            if not filepath :

                customer_name =application_data .get ('customer',{}).get ('name','Application').replace (' ','_')
                filepath =f"./reports/approval_{customer_name }_{datetime .now ().strftime ('%Y%m%d_%H%M%S')}.pdf"


            os .makedirs (os .path .dirname (filepath )if os .path .dirname (filepath )else '.',exist_ok =True )

            generator .generate_approval_report (application_data ,filepath )
            return FileResponse (filepath ,media_type ='application/pdf',
            filename =os .path .basename (filepath ))
        else :

            pdf_buffer =generator .generate_approval_report (application_data )

            return StreamingResponse (
            iter ([pdf_buffer .getvalue ()]),
            media_type ='application/pdf',
            headers ={"Content-Disposition":"attachment; filename=approval_report.pdf"}
            )

    except Exception as e :
        raise HTTPException (status_code =500 ,detail =f"Error generating PDF: {str (e )}")


@router .post ("/statistics-pdf")
async def generate_statistics_pdf_endpoint (
statistics_data :Dict [str ,Any ],
save_to_file :bool =False ,
filepath :Optional [str ]=None 
)->Response :
    """
    Generate a PDF report with approval statistics
    
    Args:
        statistics_data: Dictionary containing:
            - total_applications: int
            - period: str (e.g., "Current Month")
            - avg_processing_time: float
            - total_loan_amount: float
            - avg_loan_amount: float
            - decisions: {approved, declined, review}
            - risk_distribution: {low, medium, high}
            - emotions: {positive, neutral, negative}
            - fraud_stats: {flagged, confirmed, false_positives, ...}
            - metrics: {avg_decision_confidence, avg_processing_time, system_uptime, ...}
        save_to_file: Whether to save PDF to disk (default: False)
        filepath: Path to save PDF if save_to_file is True
    
    Returns:
        PDF file as StreamingResponse or saved file response
    """
    try :

        if 'total_applications'not in statistics_data :
            raise HTTPException (status_code =400 ,detail ="Missing total_applications in statistics data")

        generator =PDFReportGenerator ()

        if save_to_file :
            if not filepath :

                filepath =f"./reports/statistics_{datetime .now ().strftime ('%Y%m%d_%H%M%S')}.pdf"


            os .makedirs (os .path .dirname (filepath )if os .path .dirname (filepath )else '.',exist_ok =True )

            generator .generate_statistics_report (statistics_data ,filepath )
            return FileResponse (filepath ,media_type ='application/pdf',
            filename =os .path .basename (filepath ))
        else :

            pdf_buffer =generator .generate_statistics_report (statistics_data )

            return StreamingResponse (
            iter ([pdf_buffer .getvalue ()]),
            media_type ='application/pdf',
            headers ={"Content-Disposition":"attachment; filename=statistics_report.pdf"}
            )

    except Exception as e :
        raise HTTPException (status_code =500 ,detail =f"Error generating PDF: {str (e )}")


@router .get ("/sample-application-pdf")
async def sample_application_pdf ()->Response :
    """
    Generate a sample PDF report for testing purposes
    """
    try :

        sample_data ={
        "customer":{
        "name":"Rajesh Kumar",
        "id":"CUST-2025-001",
        "monthly_income":50000 ,
        "credit_score":720 
        },
        "application":{
        "loan_amount":500000 ,
        "application_date":datetime .now ().strftime ("%Y-%m-%d")
        },
        "verification":{
        "id_status":"Verified",
        "id_date":"2025-02-05",
        "income_status":"Verified",
        "income_date":"2025-02-05",
        "address_status":"Verified",
        "address_date":"2025-02-05"
        },
        "underwriting":{
        "decision":"APPROVED",
        "emi_ratio":0.35 ,
        "emi_status":"Acceptable",
        "credit_score_assessed":"Good",
        "credit_status":"Acceptable",
        "eligibility_score":0.87 ,
        "eligibility_status":"Eligible",
        "decision_confidence":0.92 
        },
        "risk":{
        "risk_band":"LOW",
        "risk_score":0.15 ,
        "repayment_risk":0.12 ,
        "repayment_assessment":"Low",
        "fraud_risk":0.08 ,
        "fraud_assessment":"Low",
        "default_probability":0.18 ,
        "default_assessment":"Low"
        },
        "offer":{
        "approved_amount":500000 ,
        "interest_rate":8.5 ,
        "tenure":60 ,
        "emi":10141.35 ,
        "total_interest":108481 ,
        "processing_fee":5000 ,
        "offer_validity":"Valid till 2025-03-08"
        },
        "feedback":{
        "assistant_reply":"Congratulations Rajesh! Your loan application has been approved. You are eligible for a personal loan of ₹500,000 at 8.5% p.a. with a monthly EMI of ₹10,141.35. Please contact us to proceed with the documentation.",
        "actions":["send_approval_email","schedule_document_collection","activate_account"]
        }
        }

        generator =PDFReportGenerator ()
        pdf_buffer =generator .generate_approval_report (sample_data )

        return StreamingResponse (
        iter ([pdf_buffer .getvalue ()]),
        media_type ='application/pdf',
        headers ={"Content-Disposition":"attachment; filename=sample_approval_report.pdf"}
        )

    except Exception as e :
        raise HTTPException (status_code =500 ,detail =f"Error generating sample PDF: {str (e )}")


@router .get ("/sample-statistics-pdf")
async def sample_statistics_pdf ()->Response :
    """
    Generate a sample statistics PDF report for testing purposes
    """
    try :

        sample_stats ={
        "total_applications":487 ,
        "period":"February 2025",
        "avg_processing_time":18.5 ,
        "total_loan_amount":102500000 ,
        "avg_loan_amount":210478 ,
        "decisions":{
        "approved":245 ,
        "declined":162 ,
        "review":80 
        },
        "risk_distribution":{
        "low":210 ,
        "medium":197 ,
        "high":80 
        },
        "emotions":{
        "positive":156 ,
        "neutral":218 ,
        "negative":113 
        },
        "fraud_stats":{
        "flagged":45 ,
        "fraud_rate":0.092 ,
        "confirmed":12 ,
        "confirmed_rate":0.025 ,
        "false_positives":33 ,
        "false_positive_rate":0.068 
        },
        "metrics":{
        "avg_decision_confidence":0.82 ,
        "avg_processing_time":18.5 ,
        "system_uptime":0.9998 ,
        "satisfaction_score":8.7 ,
        "model_accuracy":0.921 
        }
        }

        generator =PDFReportGenerator ()
        pdf_buffer =generator .generate_statistics_report (sample_stats )

        return StreamingResponse (
        iter ([pdf_buffer .getvalue ()]),
        media_type ='application/pdf',
        headers ={"Content-Disposition":"attachment; filename=sample_statistics_report.pdf"}
        )

    except Exception as e :
        raise HTTPException (status_code =500 ,detail =f"Error generating sample PDF: {str (e )}")


@router .get ("/health")
async def pdf_router_health ()->Dict [str ,str ]:
    """
    Health check endpoint for PDF report router
    """
    try :

        import reportlab 
        return {
        "status":"healthy",
        "service":"PDF Report Generation",
        "reportlab_version":reportlab .__version__ 
        }
    except ImportError :
        return {
        "status":"unhealthy",
        "service":"PDF Report Generation",
        "error":"reportlab not installed"
        }
