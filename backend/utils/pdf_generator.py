"""
PDF Report Generator Module
Generates professional PDF reports for loan applications, approvals, and statistics
"""

import io 
from datetime import datetime 
from typing import Dict ,Any ,Optional ,BinaryIO 
from reportlab .lib .pagesizes import letter ,A4 
from reportlab .lib .styles import getSampleStyleSheet ,ParagraphStyle 
from reportlab .lib .units import inch 
from reportlab .lib .colors import HexColor ,black ,white ,grey ,lightgrey 
from reportlab .platypus import SimpleDocTemplate ,Table ,TableStyle ,Paragraph ,Spacer ,PageBreak ,Image ,KeepTogether 
from reportlab .lib import colors 
from reportlab .pdfgen import canvas 


class PDFReportGenerator :
    """Generate professional PDF reports for loan applications"""

    def __init__ (self ,page_size =letter ):
        """Initialize PDF generator"""
        self .page_size =page_size 
        self .width ,self .height =page_size 
        self .styles =getSampleStyleSheet ()
        self ._setup_custom_styles ()

    def _setup_custom_styles (self ):
        """Setup custom paragraph styles"""
        self .styles .add (ParagraphStyle (
        name ='CustomTitle',
        parent =self .styles ['Heading1'],
        fontSize =24 ,
        textColor =HexColor ('#1f4788'),
        spaceAfter =12 ,
        alignment =1 
        ))

        self .styles .add (ParagraphStyle (
        name ='SectionHeader',
        parent =self .styles ['Heading2'],
        fontSize =14 ,
        textColor =HexColor ('#2563eb'),
        spaceAfter =8 ,
        spaceBefore =8 ,
        borderColor =HexColor ('#2563eb'),
        borderWidth =1 ,
        borderPadding =4 ,
        backColor =HexColor ('#f0f4ff')
        ))

        self .styles .add (ParagraphStyle (
        name ='FieldLabel',
        parent =self .styles ['Normal'],
        fontSize =10 ,
        textColor =HexColor ('#4b5563'),
        spaceAfter =2 
        ))

        self .styles .add (ParagraphStyle (
        name ='FieldValue',
        parent =self .styles ['Normal'],
        fontSize =11 ,
        textColor =black ,
        spaceAfter =6 
        ))

        self .styles .add (ParagraphStyle (
        name ='Status',
        parent =self .styles ['Normal'],
        fontSize =12 ,
        spaceAfter =8 
        ))

    def generate_approval_report (self ,application_data :Dict [str ,Any ],filepath :Optional [str ]=None )->BinaryIO :
        """
        Generate a comprehensive PDF report for a loan application
        
        Args:
            application_data: Dictionary containing customer, application, and assessment data
            filepath: Optional filepath to save the PDF
        
        Returns:
            BytesIO buffer containing the PDF or None if saved to file
        """

        buffer =io .BytesIO ()


        doc =SimpleDocTemplate (
        buffer if not filepath else filepath ,
        pagesize =self .page_size ,
        rightMargin =0.5 *inch ,
        leftMargin =0.5 *inch ,
        topMargin =0.5 *inch ,
        bottomMargin =0.5 *inch 
        )


        elements =[]


        elements .extend (self ._build_header (application_data ))
        elements .append (Spacer (1 ,0.2 *inch ))


        elements .extend (self ._build_customer_section (application_data ))
        elements .append (Spacer (1 ,0.15 *inch ))


        elements .extend (self ._build_application_section (application_data ))
        elements .append (Spacer (1 ,0.15 *inch ))


        if application_data .get ('verification'):
            elements .extend (self ._build_verification_section (application_data ))
            elements .append (Spacer (1 ,0.15 *inch ))


        if application_data .get ('risk'):
            elements .extend (self ._build_risk_section (application_data ))
            elements .append (Spacer (1 ,0.15 *inch ))


        if application_data .get ('underwriting'):
            elements .extend (self ._build_underwriting_section (application_data ))
            elements .append (Spacer (1 ,0.15 *inch ))


        if application_data .get ('offer'):
            elements .extend (self ._build_offer_section (application_data ))
            elements .append (Spacer (1 ,0.15 *inch ))


        if application_data .get ('feedback'):
            elements .extend (self ._build_feedback_section (application_data ))
            elements .append (Spacer (1 ,0.15 *inch ))


        elements .extend (self ._build_footer ())


        doc .build (elements )


        if filepath :
            return None 
        else :
            buffer .seek (0 )
            return buffer 

    def _build_header (self ,data :Dict [str ,Any ]):
        """Build report header section"""
        elements =[]


        title =Paragraph ("EY BANK - LOAN APPLICATION REPORT",self .styles ['CustomTitle'])
        elements .append (title )


        timestamp =datetime .now ().strftime ("%Y-%m-%d %H:%M:%S")
        report_info =Paragraph (f"<b>Report Generated:</b> {timestamp }",self .styles ['Normal'])
        elements .append (report_info )


        app_id =data .get ('application',{}).get ('id','N/A')
        app_id_para =Paragraph (f"<b>Application ID:</b> {app_id }",self .styles ['Normal'])
        elements .append (app_id_para )

        return elements 

    def _build_customer_section (self ,data :Dict [str ,Any ]):
        """Build customer information section"""
        elements =[]

        elements .append (Paragraph ("CUSTOMER INFORMATION",self .styles ['SectionHeader']))
        elements .append (Spacer (1 ,0.1 *inch ))

        customer =data .get ('customer',{})


        customer_data =[
        ['Field','Value'],
        ['Full Name',customer .get ('name','N/A')],
        ['Customer ID',customer .get ('id','N/A')],
        ['Email',customer .get ('email','N/A')],
        ['Phone',customer .get ('phone','N/A')],
        ['Age',str (customer .get ('age','N/A'))],
        ['Employment Type',customer .get ('employment_type','N/A')],
        ['Monthly Income',f"${customer .get ('monthly_income',0 ):,.2f}"],
        ['Annual Income',f"${customer .get ('annual_income',0 ):,.2f}"],
        ['Credit Score',str (customer .get ('credit_score','N/A'))],
        ]

        table =Table (customer_data ,colWidths =[2 *inch ,4 *inch ])
        table .setStyle (TableStyle ([
        ('BACKGROUND',(0 ,0 ),(-1 ,0 ),HexColor ('#2563eb')),
        ('TEXTCOLOR',(0 ,0 ),(-1 ,0 ),white ),
        ('ALIGN',(0 ,0 ),(-1 ,-1 ),'LEFT'),
        ('FONTNAME',(0 ,0 ),(-1 ,0 ),'Helvetica-Bold'),
        ('FONTSIZE',(0 ,0 ),(-1 ,0 ),10 ),
        ('BOTTOMPADDING',(0 ,0 ),(-1 ,0 ),8 ),
        ('BACKGROUND',(0 ,1 ),(-1 ,-1 ),HexColor ('#f9fafb')),
        ('GRID',(0 ,0 ),(-1 ,-1 ),1 ,black ),
        ('ROWBACKGROUNDS',(0 ,1 ),(-1 ,-1 ),[white ,HexColor ('#f3f4f6')]),
        ('FONTNAME',(0 ,1 ),(0 ,-1 ),'Helvetica-Bold'),
        ('FONTSIZE',(0 ,0 ),(-1 ,-1 ),9 ),
        ('ROWHEIGHT',(0 ,0 ),(-1 ,-1 ),0.25 *inch ),
        ]))

        elements .append (table )
        return elements 

    def _build_application_section (self ,data :Dict [str ,Any ]):
        """Build loan application section"""
        elements =[]

        elements .append (Paragraph ("LOAN APPLICATION DETAILS",self .styles ['SectionHeader']))
        elements .append (Spacer (1 ,0.1 *inch ))

        application =data .get ('application',{})

        app_data =[
        ['Field','Value'],
        ['Loan Amount Requested',f"${application .get ('loan_amount',0 ):,.2f}"],
        ['Loan Term (Months)',str (application .get ('loan_term','N/A'))],
        ['Purpose',application .get ('purpose','N/A')],
        ['Application Date',application .get ('application_date','N/A')],
        ['Existing Loans',str (application .get ('existing_loans_count',0 ))],
        ['Debt-to-Income Ratio',f"{application .get ('debt_to_income',0 ):.2%}"],
        ]

        table =Table (app_data ,colWidths =[2 *inch ,4 *inch ])
        table .setStyle (TableStyle ([
        ('BACKGROUND',(0 ,0 ),(-1 ,0 ),HexColor ('#2563eb')),
        ('TEXTCOLOR',(0 ,0 ),(-1 ,0 ),white ),
        ('ALIGN',(0 ,0 ),(-1 ,-1 ),'LEFT'),
        ('FONTNAME',(0 ,0 ),(-1 ,0 ),'Helvetica-Bold'),
        ('FONTSIZE',(0 ,0 ),(-1 ,0 ),10 ),
        ('BOTTOMPADDING',(0 ,0 ),(-1 ,0 ),8 ),
        ('BACKGROUND',(0 ,1 ),(-1 ,-1 ),HexColor ('#f9fafb')),
        ('GRID',(0 ,0 ),(-1 ,-1 ),1 ,black ),
        ('ROWBACKGROUNDS',(0 ,1 ),(-1 ,-1 ),[white ,HexColor ('#f3f4f6')]),
        ('FONTNAME',(0 ,1 ),(0 ,-1 ),'Helvetica-Bold'),
        ('FONTSIZE',(0 ,0 ),(-1 ,-1 ),9 ),
        ('ROWHEIGHT',(0 ,0 ),(-1 ,-1 ),0.25 *inch ),
        ]))

        elements .append (table )
        return elements 

    def _build_verification_section (self ,data :Dict [str ,Any ]):
        """Build verification status section"""
        elements =[]

        elements .append (Paragraph ("VERIFICATION STATUS",self .styles ['SectionHeader']))
        elements .append (Spacer (1 ,0.1 *inch ))

        verification =data .get ('verification',{})

        verification_data =[
        ['Verification Type','Status'],
        ['Identity Verification',verification .get ('id_status','Pending')],
        ['Income Verification',verification .get ('income_status','Pending')],
        ['Address Verification',verification .get ('address_status','Pending')],
        ['Employment Verification',verification .get ('employment_status','Pending')],
        ['Document Verification',verification .get ('document_status','Pending')],
        ]

        table =Table (verification_data ,colWidths =[3 *inch ,3 *inch ])
        table .setStyle (TableStyle ([
        ('BACKGROUND',(0 ,0 ),(-1 ,0 ),HexColor ('#059669')),
        ('TEXTCOLOR',(0 ,0 ),(-1 ,0 ),white ),
        ('ALIGN',(0 ,0 ),(-1 ,-1 ),'CENTER'),
        ('FONTNAME',(0 ,0 ),(-1 ,0 ),'Helvetica-Bold'),
        ('FONTSIZE',(0 ,0 ),(-1 ,0 ),10 ),
        ('BOTTOMPADDING',(0 ,0 ),(-1 ,0 ),8 ),
        ('BACKGROUND',(0 ,1 ),(-1 ,-1 ),HexColor ('#f0fdf4')),
        ('GRID',(0 ,0 ),(-1 ,-1 ),1 ,black ),
        ('ROWBACKGROUNDS',(0 ,1 ),(-1 ,-1 ),[white ,HexColor ('#f0fdf4')]),
        ('FONTSIZE',(0 ,0 ),(-1 ,-1 ),9 ),
        ('ROWHEIGHT',(0 ,0 ),(-1 ,-1 ),0.25 *inch ),
        ]))

        elements .append (table )
        return elements 

    def _build_risk_section (self ,data :Dict [str ,Any ]):
        """Build risk assessment section"""
        elements =[]

        elements .append (Paragraph ("RISK ASSESSMENT",self .styles ['SectionHeader']))
        elements .append (Spacer (1 ,0.1 *inch ))

        risk =data .get ('risk',{})

        risk_data =[
        ['Parameter','Value'],
        ['Risk Band',risk .get ('risk_band','N/A')],
        ['Risk Score',f"{risk .get ('risk_score',0 ):.2f}"],
        ['Confidence',f"{risk .get ('confidence',0 ):.2%}"],
        ['Repayment Risk',risk .get ('repayment_risk','N/A')],
        ['Fraud Risk',risk .get ('fraud_risk','N/A')],
        ['Delinquency (12M)',str (risk .get ('delinquency_12m',0 ))],
        ['Outstanding Debt',f"${risk .get ('outstanding_debt',0 ):,.2f}"],
        ['Hard Inquiries',str (risk .get ('num_hard_inquiries',0 ))],
        ]

        table =Table (risk_data ,colWidths =[2 *inch ,4 *inch ])


        risk_band =risk .get ('risk_band','MEDIUM').upper ()
        if 'LOW'in risk_band :
            header_color =HexColor ('#059669')
        elif 'HIGH'in risk_band :
            header_color =HexColor ('#dc2626')
        else :
            header_color =HexColor ('#d97706')

        table .setStyle (TableStyle ([
        ('BACKGROUND',(0 ,0 ),(-1 ,0 ),header_color ),
        ('TEXTCOLOR',(0 ,0 ),(-1 ,0 ),white ),
        ('ALIGN',(0 ,0 ),(-1 ,-1 ),'LEFT'),
        ('FONTNAME',(0 ,0 ),(-1 ,0 ),'Helvetica-Bold'),
        ('FONTSIZE',(0 ,0 ),(-1 ,0 ),10 ),
        ('BOTTOMPADDING',(0 ,0 ),(-1 ,0 ),8 ),
        ('BACKGROUND',(0 ,1 ),(-1 ,-1 ),HexColor ('#fafafa')),
        ('GRID',(0 ,0 ),(-1 ,-1 ),1 ,black ),
        ('ROWBACKGROUNDS',(0 ,1 ),(-1 ,-1 ),[white ,HexColor ('#f3f4f6')]),
        ('FONTNAME',(0 ,1 ),(0 ,-1 ),'Helvetica-Bold'),
        ('FONTSIZE',(0 ,0 ),(-1 ,-1 ),9 ),
        ('ROWHEIGHT',(0 ,0 ),(-1 ,-1 ),0.25 *inch ),
        ]))

        elements .append (table )
        return elements 

    def _build_underwriting_section (self ,data :Dict [str ,Any ]):
        """Build underwriting decision section"""
        elements =[]

        elements .append (Paragraph ("UNDERWRITING DECISION",self .styles ['SectionHeader']))
        elements .append (Spacer (1 ,0.1 *inch ))

        underwriting =data .get ('underwriting',{})
        decision =underwriting .get ('decision','PENDING').upper ()


        if 'APPROVE'in decision :
            status_color =HexColor ('#059669')
            text_color ='#059669'
        elif 'DECLINE'in decision :
            status_color =HexColor ('#dc2626')
            text_color ='#dc2626'
        else :
            status_color =HexColor ('#d97706')
            text_color ='#d97706'


        status_text =f"<font color='{text_color }'><b>{decision }</b></font>"
        status_para =Paragraph (f"Decision: {status_text }",self .styles ['Status'])
        elements .append (status_para )
        elements .append (Spacer (1 ,0.1 *inch ))

        underwriting_data =[
        ['Parameter','Value'],
        ['EMI Ratio',f"{underwriting .get ('emi_ratio',0 ):.2%}"],
        ['Decision Confidence',f"{underwriting .get ('decision_confidence',0 ):.2%}"],
        ['Processing Status',underwriting .get ('processing_status','N/A')],
        ['Underwriter Comments',underwriting .get ('comments','N/A')],
        ]

        table =Table (underwriting_data ,colWidths =[2 *inch ,4 *inch ])
        table .setStyle (TableStyle ([
        ('BACKGROUND',(0 ,0 ),(-1 ,0 ),status_color ),
        ('TEXTCOLOR',(0 ,0 ),(-1 ,0 ),white ),
        ('ALIGN',(0 ,0 ),(-1 ,-1 ),'LEFT'),
        ('VALIGN',(0 ,0 ),(-1 ,-1 ),'TOP'),
        ('FONTNAME',(0 ,0 ),(-1 ,0 ),'Helvetica-Bold'),
        ('FONTSIZE',(0 ,0 ),(-1 ,0 ),10 ),
        ('BOTTOMPADDING',(0 ,0 ),(-1 ,0 ),8 ),
        ('BACKGROUND',(0 ,1 ),(-1 ,-1 ),HexColor ('#fafafa')),
        ('GRID',(0 ,0 ),(-1 ,-1 ),1 ,black ),
        ('ROWBACKGROUNDS',(0 ,1 ),(-1 ,-1 ),[white ,HexColor ('#f3f4f6')]),
        ('FONTSIZE',(0 ,0 ),(-1 ,-1 ),9 ),
        ('ROWHEIGHT',(0 ,0 ),(-1 ,-1 ),0.3 *inch ),
        ]))

        elements .append (table )
        return elements 

    def _build_offer_section (self ,data :Dict [str ,Any ]):
        """Build loan offer section"""
        elements =[]

        elements .append (Paragraph ("APPROVED OFFER DETAILS",self .styles ['SectionHeader']))
        elements .append (Spacer (1 ,0.1 *inch ))

        offer =data .get ('offer',{})

        offer_data =[
        ['Detail','Amount/Value'],
        ['Approved Loan Amount',f"${offer .get ('approved_amount',0 ):,.2f}"],
        ['Interest Rate',f"{offer .get ('interest_rate',0 ):.2f}%"],
        ['Loan Tenure (Months)',str (offer .get ('tenure','N/A'))],
        ['Monthly EMI',f"${offer .get ('emi',0 ):,.2f}"],
        ['Processing Fee',f"${offer .get ('processing_fee',0 ):,.2f}"],
        ['Total Amount Payable',f"${offer .get ('total_payable',0 ):,.2f}"],
        ['Offer Validity',offer .get ('offer_validity','N/A')],
        ]

        table =Table (offer_data ,colWidths =[2.5 *inch ,3.5 *inch ])
        table .setStyle (TableStyle ([
        ('BACKGROUND',(0 ,0 ),(-1 ,0 ),HexColor ('#0891b2')),
        ('TEXTCOLOR',(0 ,0 ),(-1 ,0 ),white ),
        ('ALIGN',(0 ,0 ),(-1 ,-1 ),'LEFT'),
        ('FONTNAME',(0 ,0 ),(-1 ,0 ),'Helvetica-Bold'),
        ('FONTSIZE',(0 ,0 ),(-1 ,0 ),10 ),
        ('BOTTOMPADDING',(0 ,0 ),(-1 ,0 ),8 ),
        ('BACKGROUND',(0 ,1 ),(-1 ,-1 ),HexColor ('#f0f9fa')),
        ('GRID',(0 ,0 ),(-1 ,-1 ),1 ,black ),
        ('ROWBACKGROUNDS',(0 ,1 ),(-1 ,-1 ),[white ,HexColor ('#cffafe')]),
        ('FONTNAME',(0 ,1 ),(0 ,-1 ),'Helvetica-Bold'),
        ('FONTSIZE',(0 ,0 ),(-1 ,-1 ),9 ),
        ('ROWHEIGHT',(0 ,0 ),(-1 ,-1 ),0.25 *inch ),
        ]))

        elements .append (table )
        return elements 

    def _build_feedback_section (self ,data :Dict [str ,Any ]):
        """Build feedback and comments section"""
        elements =[]

        elements .append (Paragraph ("FEEDBACK & RECOMMENDATIONS",self .styles ['SectionHeader']))
        elements .append (Spacer (1 ,0.1 *inch ))

        feedback =data .get ('feedback',{})

        if feedback .get ('assistant_reply'):
            reply_para =Paragraph (
            f"<b>AI Assistant Response:</b><br/>{feedback .get ('assistant_reply','N/A')}",
            self .styles ['Normal']
            )
            elements .append (reply_para )
            elements .append (Spacer (1 ,0.08 *inch ))

        if feedback .get ('actions'):
            actions =feedback .get ('actions',[])
            if actions :
                actions_text ="<b>Recommended Actions:</b><br/>"
                for i ,action in enumerate (actions ,1 ):
                    actions_text +=f"{i }. {action }<br/>"

                actions_para =Paragraph (actions_text ,self .styles ['Normal'])
                elements .append (actions_para )
                elements .append (Spacer (1 ,0.08 *inch ))

        if feedback .get ('next_steps'):
            steps_para =Paragraph (
            f"<b>Next Steps:</b><br/>{feedback .get ('next_steps','N/A')}",
            self .styles ['Normal']
            )
            elements .append (steps_para )

        return elements 

    def _build_footer (self ):
        """Build document footer"""
        elements =[]

        elements .append (Spacer (1 ,0.2 *inch ))

        footer_text =(
        "<b>Important Notice:</b> This report is confidential and intended solely for authorized personnel. "
        "Unauthorized distribution is prohibited. All information contained herein is subject to applicable "
        "privacy and data protection regulations."
        )

        footer_para =Paragraph (footer_text ,self .styles ['Normal'])
        elements .append (footer_para )

        elements .append (Spacer (1 ,0.1 *inch ))

        signature_text =(
        "Prepared by: EY Agentic AI System<br/>"
        f"Report Date: {datetime .now ().strftime ('%B %d, %Y at %I:%M %p')}<br/>"
        "Powered by Advanced Machine Learning & AI Agents"
        )

        signature_para =Paragraph (signature_text ,self .styles ['Normal'])
        elements .append (signature_para )

        return elements 

    def generate_statistics_report (self ,statistics_data :Dict [str ,Any ],filepath :Optional [str ]=None )->BinaryIO :
        """
        Generate a PDF report with approval statistics and metrics
        
        Args:
            statistics_data: Dictionary containing statistics and metrics
            filepath: Optional filepath to save the PDF
        
        Returns:
            BytesIO buffer containing the PDF or None if saved to file
        """
        buffer =io .BytesIO ()

        doc =SimpleDocTemplate (
        buffer if not filepath else filepath ,
        pagesize =self .page_size ,
        rightMargin =0.5 *inch ,
        leftMargin =0.5 *inch ,
        topMargin =0.5 *inch ,
        bottomMargin =0.5 *inch 
        )

        elements =[]


        title =Paragraph ("EY BANK - STATISTICS & METRICS REPORT",self .styles ['CustomTitle'])
        elements .append (title )

        timestamp =datetime .now ().strftime ("%Y-%m-%d %H:%M:%S")
        report_info =Paragraph (f"<b>Report Generated:</b> {timestamp }",self .styles ['Normal'])
        elements .append (report_info )
        elements .append (Spacer (1 ,0.2 *inch ))


        elements .append (Paragraph ("SUMMARY STATISTICS",self .styles ['SectionHeader']))
        elements .append (Spacer (1 ,0.1 *inch ))

        summary_data =[
        ['Metric','Value'],
        ['Total Applications',str (statistics_data .get ('total_applications',0 ))],
        ['Period',statistics_data .get ('period','N/A')],
        ['Avg Processing Time (hours)',f"{statistics_data .get ('avg_processing_time',0 ):.2f}"],
        ['Total Loan Amount',f"${statistics_data .get ('total_loan_amount',0 ):,.2f}"],
        ['Average Loan Amount',f"${statistics_data .get ('avg_loan_amount',0 ):,.2f}"],
        ]

        table =Table (summary_data ,colWidths =[3 *inch ,3 *inch ])
        table .setStyle (TableStyle ([
        ('BACKGROUND',(0 ,0 ),(-1 ,0 ),HexColor ('#2563eb')),
        ('TEXTCOLOR',(0 ,0 ),(-1 ,0 ),white ),
        ('ALIGN',(0 ,0 ),(-1 ,-1 ),'LEFT'),
        ('FONTNAME',(0 ,0 ),(-1 ,0 ),'Helvetica-Bold'),
        ('FONTSIZE',(0 ,0 ),(-1 ,0 ),10 ),
        ('BOTTOMPADDING',(0 ,0 ),(-1 ,0 ),8 ),
        ('GRID',(0 ,0 ),(-1 ,-1 ),1 ,black ),
        ('ROWBACKGROUNDS',(0 ,1 ),(-1 ,-1 ),[white ,HexColor ('#f3f4f6')]),
        ('FONTSIZE',(0 ,0 ),(-1 ,-1 ),9 ),
        ('ROWHEIGHT',(0 ,0 ),(-1 ,-1 ),0.25 *inch ),
        ]))

        elements .append (table )
        elements .append (Spacer (1 ,0.2 *inch ))


        elements .append (Paragraph ("DECISIONS DISTRIBUTION",self .styles ['SectionHeader']))
        elements .append (Spacer (1 ,0.1 *inch ))

        decisions =statistics_data .get ('decisions',{})
        decisions_data =[
        ['Decision Type','Count'],
        ['Approved',str (decisions .get ('approved',0 ))],
        ['Declined',str (decisions .get ('declined',0 ))],
        ['Under Review',str (decisions .get ('review',0 ))],
        ]

        table =Table (decisions_data ,colWidths =[2.5 *inch ,2.5 *inch ])
        table .setStyle (TableStyle ([
        ('BACKGROUND',(0 ,0 ),(-1 ,0 ),HexColor ('#059669')),
        ('TEXTCOLOR',(0 ,0 ),(-1 ,0 ),white ),
        ('ALIGN',(0 ,0 ),(-1 ,-1 ),'CENTER'),
        ('FONTNAME',(0 ,0 ),(-1 ,0 ),'Helvetica-Bold'),
        ('GRID',(0 ,0 ),(-1 ,-1 ),1 ,black ),
        ('ROWBACKGROUNDS',(0 ,1 ),(-1 ,-1 ),[white ,HexColor ('#f0fdf4')]),
        ('FONTSIZE',(0 ,0 ),(-1 ,-1 ),9 ),
        ('ROWHEIGHT',(0 ,0 ),(-1 ,-1 ),0.25 *inch ),
        ]))

        elements .append (table )
        elements .append (Spacer (1 ,0.2 *inch ))


        elements .append (Paragraph ("RISK DISTRIBUTION",self .styles ['SectionHeader']))
        elements .append (Spacer (1 ,0.1 *inch ))

        risk_dist =statistics_data .get ('risk_distribution',{})
        risk_data =[
        ['Risk Level','Count'],
        ['Low Risk',str (risk_dist .get ('low',0 ))],
        ['Medium Risk',str (risk_dist .get ('medium',0 ))],
        ['High Risk',str (risk_dist .get ('high',0 ))],
        ]

        table =Table (risk_data ,colWidths =[2.5 *inch ,2.5 *inch ])
        table .setStyle (TableStyle ([
        ('BACKGROUND',(0 ,0 ),(-1 ,0 ),HexColor ('#d97706')),
        ('TEXTCOLOR',(0 ,0 ),(-1 ,0 ),white ),
        ('ALIGN',(0 ,0 ),(-1 ,-1 ),'CENTER'),
        ('FONTNAME',(0 ,0 ),(-1 ,0 ),'Helvetica-Bold'),
        ('GRID',(0 ,0 ),(-1 ,-1 ),1 ,black ),
        ('ROWBACKGROUNDS',(0 ,1 ),(-1 ,-1 ),[white ,HexColor ('#fffbeb')]),
        ('FONTSIZE',(0 ,0 ),(-1 ,-1 ),9 ),
        ('ROWHEIGHT',(0 ,0 ),(-1 ,-1 ),0.25 *inch ),
        ]))

        elements .append (table )
        elements .append (Spacer (1 ,0.15 *inch ))


        footer_text =(
        f"Report Period: {statistics_data .get ('period','N/A')}<br/>"
        f"Total Applications Processed: {statistics_data .get ('total_applications',0 )}"
        )
        footer_para =Paragraph (footer_text ,self .styles ['Normal'])
        elements .append (footer_para )


        doc .build (elements )

        if filepath :
            return None 
        else :
            buffer .seek (0 )
            return buffer 



def generate_application_pdf (application_data :Dict [str ,Any ],filepath :Optional [str ]=None )->BinaryIO :
    """Generate an application approval PDF"""
    generator =PDFReportGenerator ()
    return generator .generate_approval_report (application_data ,filepath )


def generate_statistics_pdf (statistics_data :Dict [str ,Any ],filepath :Optional [str ]=None )->BinaryIO :
    """Generate a statistics PDF"""
    generator =PDFReportGenerator ()
    return generator .generate_statistics_report (statistics_data ,filepath )
