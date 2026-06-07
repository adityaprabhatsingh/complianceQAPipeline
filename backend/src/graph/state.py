from ast import operator
from types import AsyncGeneratorType
import operator
from typing import Annotated,List,Dict,Optional,Any,TypedDict



#this give a error report 
#this also prevent the ai to give a unstructured text that frontend connot display
class ComplianceIssues(TypedDict):
    category : str
    description : str #specific detail of teh violences
    severity : str #critical and warning

    timestamp : Optional[str]

#define the global graph state 
#this define the state that get passed around in the agentic workflow 
class VideoAuditState(TypedDict):
    ''' 
    define the data schema for the langgraph execution content
    it is like a main containner that hold the all the data of audit process to initial url to final report 
    '''

    #imput parameter
    video_url=str
    video_id= str # this is very useful for azure video indexer

    #ingestion and extration
    #this content all the data related to the video
    local_file_path=Optional[str]# location where the video temporaly stored
    video_metadata=Dict[str,Any]  #{::15,"quality":1080p}.   {technical detail }
    transcript=Optional[str] # fully extrated video to text
    ocr_text=List[str] # it hold the text that appear on the screen visually 


    #analysis output
    # this store all the violation found by the azure openai 
    compliances_result=Annotated[List[ComplianceIssues],operator.add]# if node return a issues then added to the operator (issues list)

    #final observation 
    final_status=str # marks pass|fail
    final_report =str#markdown format


    #system observability
    #error: API timeout ,systemlevel error 
    #list of the system level crashes 
    error=Annotated[List[str],operator.add]

  







