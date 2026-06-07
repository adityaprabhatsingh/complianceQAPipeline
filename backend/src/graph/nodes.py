from langchain_core.tools import retriever
import json 
import os 
import logging
import re # for regular expression
from typing import Dict ,Any,List

from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from langchain_community.vectorstores import AzureSearch
from langchain_core.prompts import ChatMessagePromptTemplate
from langchain_core.messages import HumanMessage,SystemMessage

#import the the function from the state file (schema)

from backend.src.graph.state import VideoAuditState,ComplianceIssues


# import service
from backend.src.services.video_indexer import VideoIndexerServices


#configure logger (Logger → records the error details)

logger=logging.getLogger("brand-guardian")
logging.basicConfig(level=logging.INFO)

# NODE 1 
#this function is reponsible for converting the video to the text
#VideoAuditState. this content the youtube url 
def index_video_node(state:VideoAuditState)-> Dict[str,Any]:
    '''
    Download the youtube video from the url 
    Uplaod to the azure Video Indexer
    extract the insight 
    '''
    video_url=state.get("video_url")
    video_id_input=state.get("video_id","vid_demo")
    logger.info(f"---[Node:Indexer]--processing:{video_url}")

    local_filename="temp_audit_video.mp4"

    try:
        vi_service=VideoIndexerServices()
        #downoad. yt=dlp. use for download a video from the youtube
        if "youtube.com" in video_url or "youtu.be" in video_url:
            local_path=vi_service.downlaod_youtube_video(video_url,output_path=local_filename)
        else:
            raise Exception("Please enter the valid vedio url")


        #upload
        # this send the local downlaod video to the azure 
        azure_video_id=vi_service.upload_video(local_path,video_name=video_id_input)
        logger.info(f"Upload success. Azure ID ={azure_video_id} ")


        #clean up 
        if os.path.exist(local_path):
            os.remove(local_path)

        #wait 
        # ut stop the code and asking the azure are u done in every 30 sec(gerneral take 5 to 10 min azure )
        raw_insight=vi_service.wait_for_processing(azure_video_id)

        #extract
        #this pull the data that needed 
        clean_data=vi_service.extract_data(raw_insight)
        logger.info("---[NODE: Indexer ] Extraction completed -----")
        return clean_data

    except Exception as e:
        logger.error(f"---Video Indexer Failed:{e}")

        return{
            "error" : [str(e)],
            "final_status" : "FAIL",
            "transcript" : "",
            "ocr_text" : []

            }


#NODE 2 : compliance Auditor
# this help the ai to judge the content 
#now this VideoAuditState. contain a teanscript and ocr text 
def audit_content_mode(state:VideoAuditState)-> Dict[str,Any]:
    '''
    perform a retrieval Augmnent generation(RAG) to audit the content =brand video

    '''

    logger.info("---[Node:Audit] querying the knowleadge base & LLM")
    transcript=state.get("transcript","")# return the transcript or the empty
    if not transcript:
        logger.warning("no transcript available.  skipping audit......")
        return{
            "final_status" : "FAIL",
            "final_report" : "Audit Skipped because video processing failed(no Transcript)"


        }
    
    #initialize the LLM
    llm= AzureChatOpenAI(
        azure_deployment=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT"),
        openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        temperature=0.0)

    
    embedding=AzureOpenAIEmbeddings(
        azure_deployment="text-embedding-3-small",
        openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION")

    )

    vector_store=AzureSearch(
        azure_search_endpoint=os.getenv("AZURE_SEARCH_ENDPOINT")
        azure_search_api_key=os.getenv("AZURE_SEARCH_API_KEY")
        index_name=os.getenv("AZURE_SEARCH_INDEX_NAME")
        embedding_function=embedding.embed_query

    )

    #RAG retrieval
    ocr_text=state.get("ocr.txt",[])
    query_text=f"{transcript} {''.join(ocr_text)}"
    docs=vector_store.similarity_search(query_text,k=3)
    #it asked the azure to find the 3 relavant pages from pdf rule book matching the text
    #and join this pages  and store into a varible retrieved_rules
    retrieved_rules="/n/n".join([doc.page_content for doc in docs])

     # instead for sending the whole the whole pdf which become a explensive we send only the 3 relavant pages 

    system_prompt=f"""
    you are a brand safety compliance auditor
    OFFICIAL REGULATORY RULES:
    {retrieved_rules}
    INSTRUCTION:
    1. Analyzes the Transcript and OCR text below 
    2. Identify any violation of the rule
    3. return strictly JSON in the following format:
        {{
        "compliance_results": [
            {{
                "category": "Claim Validation",
                "severity": "CRITICAL",
                "description": "Explanation of the violation..."
            }}
        ],
        "status": "FAIL", 
        "final_report": "Summary of findings..."
    }}
    If no violations are found, set "status" to "PASS" and "compliance_results" to [].
    """

    user_message = f"""
    VIDEO METADATA: {state.get('video_metadata', {})}
    TRANSCRIPT: {transcript}
    ON-SCREEN TEXT (OCR): {ocr_text}
    """


    try:
        response=llm.revoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message)

        ])
        content=response.content

        audit_data=Json.load(content.strip())
        return{
            "compliances_result":audit_data.get("compliances_result",[]),
            "final_status":audit_data.get("status","FAIL"),
            "final_report":audit_data.get("final_report","no report is gernated")
        }
    except Exception as e:
        logger.error(f"system Error in audit node{str(e)}")

        #logging the raw response
        logger.error(f"Raw llm response : {response.content if 'response' in locals() else 'None'}")
        return{
            "error" : [str(e)],
            "final_status" : "FAIL",

        }



   
    

       

        

        

        

        


        
    



    








    

