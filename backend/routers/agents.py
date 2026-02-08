from fastapi import APIRouter 
from agents .sales_persuasion import router as sales_router 

router =APIRouter ()
router .include_router (sales_router )
