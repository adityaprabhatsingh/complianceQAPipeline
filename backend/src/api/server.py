# write a fastapi code

from fastapi import status
from opentelemetry._logs import severity
from unicodedata import category
from distro import version
from numpy._core.defchararray import title
import uuid
import logging
from fastapi import FastAPI ,HTTPException


from pydantic import BaseModel
from typing import List,Optional

# load the enviroment variable 
from dotenv import load_dotenv
load_dotenv(override=True)


# initilsed the telementry 
from backend.src.api.telementry import setup_telemetry
setup_telemetry()

# import workflow graph (langgraph)

from backend.src.graph.workflow import app as compliance_graph # to avpid the confusion e=with fast api app we rename the app to compliance_graph 

# configure logging

logging.basicConfig(level=logging.INFO)
logger=logging.getLogger("api-server")


# create a fastapi application 
app =FASTAPI(
    title= "Brand Guardian AI API",
    description= "API auditing video content againist the brand compiances ",
    version="1.0.0"


)

# we define a data model(pydantic model )
class AuditRequest(BaseModel):
    """
    DEfine the expected structure of the incoming API request 
    Example valid request
    {"https://www.youtube.com/watch?v=I3CWFDgqvq8"}

    invalid request:
    {"1335"}
    """

    video_url:str

class ComplianceIssue(BaseModel):
    category:str
    severity: str
    description:str

class AuditResponse(BaseModel):
    session_id:str
    video_id: str
    status:str
    final_status:str
    compliance_status:List[ComplianceIssue]

# difine the main endpoint 
@app.post("/audit",response_model=AuditResponse)

async def audit_video(request:AuditResponse):
    """
    main api endpoint that tigger the compliances audit workflow 
    """
    session_id=str(uuid.uuid4())
    video_id_short=f"vid_{session_id[:8]}"
    logger.info(f"Recieved the Audit Response :{request.video_url}(session:{session_id})")

    # graph input 
    initial_input={
        "video_url":request.video_url,
        "video_id": video_id_short,
        "compliance_results":[],
        "error":[]
    }

    try:
        final_state=compliance_graph.invoke(initial_input)
        return AuditResponse(
            session_id=session_id,
            video_id=final_state.get("video_id"),
            status=final_state.get("final_status","UNKNOWN"),
            final_report=final_state.get("final_report","no gernated report yet" ),
            compliance_graph=final_state.get("compliance_results",[])



        )
    except Exception as e:
        logger.error(f"Audit failed:{str(e)}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# check health endpoint

@app.get("/health")

def health_check():
    ''' check the status of the compliance
    '''
    return {"status": "healthy","service":"Brand Guardian Ai"}







