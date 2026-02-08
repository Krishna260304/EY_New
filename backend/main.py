from fastapi import FastAPI 
import torch 
import signal 
import sys 
from utils .gpu_utils import setup_gpu_environment ,get_device_manager 
from ml .gpu_accelerated_inference import accelerator 


setup_gpu_environment ()
device_manager =get_device_manager ()

from routers import crm 
from routers import credit_score 
from routers import agents 
from routers import eligibility 
from routers import risk 
from routers import offer 
from routers import supervisor_route 
from routers .feedback_router import router as feedback_router 
from routers .orchestrator import router as orchestrator_router 
from routers .pdf_report import router as pdf_report_router 
from routers import auth 


if torch .cuda .is_available ():
    HF_DEVICE =0 
elif hasattr (torch ,"xpu")and torch .xpu .is_available ():
    HF_DEVICE =0 
else :
    HF_DEVICE =-1 


app =FastAPI (
title ="Agentic AI Backend",
version ="1.0.0",
description ="Advanced AI-powered lending platform with multi-agent orchestration - GPU/NPU Accelerated"
)

app .include_router (crm .router )
app .include_router (credit_score .router )
app .include_router (agents .router )
app .include_router (eligibility .router )
app .include_router (risk .router )
app .include_router (offer .router )
app .include_router (supervisor_route .router )
app .include_router (feedback_router )
app .include_router (orchestrator_router )
app .include_router (pdf_report_router )
app .include_router (auth .router )


@app .get ("/")
def root ():
    device_info =accelerator .get_device_info ()
    device_info ["device_manager"]={
    "primary_device":str (device_manager .get_device ()),
    "gpu_device":str (device_manager .gpu_device )if device_manager .gpu_device else None ,
    "npu_device":str (device_manager .npu_device )if device_manager .npu_device else None ,
    "hybrid_available":device_manager .is_hybrid_available (),
    "dtype":str (device_manager .get_dtype ()),
    "cuda_version":device_manager .cuda_version 
    }
    return {
    "message":"Agentic AI Backend running - GPU/NPU ACCELERATED",
    "version":"1.0.0",
    "acceleration":device_info 
    }


@app .get ("/health")
def health_check ():
    return {
    "status":"healthy",
    "service":"agentic-ai-backend",
    "gpu_enabled":torch .cuda .is_available (),
    "device":str (device_manager .get_device ())
    }


def signal_handler (sig ,frame ):
    sys .exit (0 )

signal .signal (signal .SIGINT ,signal_handler )
