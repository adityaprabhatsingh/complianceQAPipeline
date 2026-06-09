"""
connector : btw python and azure video indexer
"""

from sqlalchemy import false
from aiohttp import request
from openai.types.responses import response
from httpcore import URL
import yt_dlp
import logging
import os 
import logging
import time 
import requests
import yt_dlp
#it is a global key which fond a best way to log you to azure 
from azure.identity import DefaultAzureCredential


logger =logging.getLogger("video_indexer")

class VideoIndexerService:
    #setup face read all env variable (gather necesary work )
    def __init__(self):
        self.account_id=os.getenv("VIDEO_INDEXER_ACCOUNT_ID")
        self.location=os.getenv("AZURE_VI_LOCATION")
        self.subcription_id=os.getenv("AZURE_SUBSCRIPTION_ID")
        self.resource_group=os.getenv("AZURE_RESOURCE_GROUP")
        self.vi_name=os.getenv("AZURE_VI_NAME","project-brand-guardian-001")
        self.credential=DefaultAzureCredential()
        
    def get_access_token(self):
        """
        Gernate a ARM token


        it simply aviabke code simply copy paste from azure docs
        it give a temporay pass to who i am  procve your identity 
        """
        try:
            token_object= self.credential.get_token("https://management.azure.com/.default")
            return token_object.token
        except Exception as e:
            logger.error(f"failed to get azure token :{str(e)}")
            raise

    def get_account_token(self,arm_acess_token):
        """
        pass the genates token to azure video indexer
        Exchnage the ARM token for video indexer accoount team 
        """
        # ready made code 
        url = (
            f"https://management.azure.com/subscriptions/{self.subscription_id}"
            f"/resourceGroups/{self.resource_group}"
            f"/providers/Microsoft.VideoIndexer/accounts/{self.vi_name}"
            f"/generateAccessToken?api-version=2024-01-01"

        )
        headers = {"Authorization": f"Bearer {arm_access_token}"}
        payload = {"permissionType": "Contributor", "scope": "Account"}
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code != 200:
            raise Exception(f"Failed to get VI Account Token: {response.text}")
        return response.json().get("accessToken")

    # function to download a youtube video 
    def download_youtube_video(self,url,output_path="temp_video.mp4"):
        """
        download a youtube vedio to local file 
        """
        logger.info(f"downloading a youtube video{url}")
# this code avaible on the docs 
        ytl_opts={
            "format" : 'best ',
            'outtmpl' : output_path,
            'quiet' : false,
            'overwrites' : false,
            'extractor_args': {'youtube': {'player_client': ['android', 'web']}}, # mean try the android fist the fall back to web 
            'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }# this making sure what brozer making the request 

    }
        # azure video indexer cannot directly access the youtbe so downloaded needed
        #tell the yt_dlp to downlaod a youtube video 
        try:
            with yt_dlp.YoutubeDL(ytl_opts) as ydl:
                ydl.download([url])
            logger.info(f"download complete")

            return output_path

        except Exception as e:
            raise Exception(f"youtube video downlaoded failed : {str(e)}")
        

    #uplaod a video to azure video indexer 
    def upload_video(self, video_path,video_name):
        # this 2 line check that key are fresh 
        arm_token=self.get_access_token()
        vi_token=self.get_account_token(arm_token)



        api_url=f"https://api.videoindexer.ai/{self.location}/Account/{self.account_id}/Videos"
        params={
            #instrauction for the azure 
            "access_token": vi_token,
            "name" : video_name,
            "privacy" : "Private",
            "indexingPresent" : "Default"

        }
        logger.info(f"uploading file{video_path} to azure ")
        #opening the video and get access to the azure 
        #open afile in binary  and stream it on azure (upper link)
        with open(video_path,'rb') as video_file :
            files={'file': video_file}
            # uplaod a vodeo to azure 
            response= requests.post(api_url,params=params,files=files)

        if response.status_code != 200:
            raise Exception(f"azure upload failed : {response.text}")
   
   # this function contain the processing happen in the azure 
    def wait_for_processsing(self,video_id):
        # waiting time where all the process taking place
        logger.info(f"waiting for the video {video_id} to process ......")
        while True:
            arm_token=self.get_access_token()
            vi_token=self.get_account_token(arm_token)

            url=f"https://api.videoindexer.ai/{self.location}/Account/{self.account_id}/Videos"
            params={"accessToken" : vi_token}
            response= requests.get(url,params=params)
            data=response.json()

            state= data.get('state')
            if state =="Processed":
                return data
            elif state=="Failed":
                raise Exception("video Indexer failed in azure ")

            logger.info(f"state:{state}..... waiting ")

            time.sleep(30)
    # extract the data which is in json format

    # azure return a large data which conatian timestamp phase codiante so we will wxtract only the transcript and ocr part

    def extract_data(self,vi_json):
        'parses the json format into a state format'
        transcript_lines=[]
     #get the transcript part 
        for v in vi_json.get("videos",[]):
            #from entire file we only want a transcript parrt
            for insight in v.get("insight",{}).get("transcript",[]):
                transcript_lines.append(insight.get("text"))
        
        # get a ocr part from azure return

        ocr_lines = []
        for v in vi_json.get("videos",[]):
            for insight in v.get("insight",{}).get("ocr",[]):
                ocr_lines.append(insight.get("text"))

        return{
            "transcript" :" ".join(transcript_lines),
           "ocr_text" : ocr_lines,
           "video_metadata":{
            "duration": vi_json.get("summarizedInsight,{}").get("duration"),
            "platform" : "youtube"
           }
        }
        



        










    



        
        


        
        
    



       

        

        
