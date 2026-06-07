from langchain_community.docstore import document
from openai.types import vector_store
from requests.models import ITER_CHUNK_SIZE
from langchain_openai import AzureOpenAIEmbeddings
from openai import azure_endpoint
from sqlalchemy.engine.characteristics import LoggingTokenCharacteristic
import os
import glob #help us to read a file 
import logging
from dotenv import load_dotenv
load_dotenv(override=True)

#document loading and splitting
from langchain_community.document_loaders import PyPDFLoader# this open and read a pdf file
from langchain_text_splitters import RecursiveCharacterTextSplitter# this split the large data into small pieces
 

# azure component import 
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import AzureSearch



#setup logging
#this is global logging copy this from docs
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s - %(message)s"
)
logger=logging.getLogger("indexer")

def index_doc():
    '''
    Read the PDF file , Chunk them  and uplaod them to the azure ai search 
    '''

    #define the path ,we look for the data folder
    #it is search for the path 
    current_dir= os.path.dirname(os.path.abspath(__file__))
    data_folder=os.path.join(current_dir,"../../backend/data")

    #check the environment variable

    logger.info("="*60)
    logger.info("Enviroment congigurarion check")
    logger.info(f"AZURE_OPENAI_ENDPOINT : {os.getenv('AZURE_OPENAI_ENDPOINT')}")
    logger.info(f"AZURE_OPENAI_API_VERSION : {os.getenv('AZURE_OPENAI_API_VERSION')}")
    logger.info(f"Embedding deployment  : {os.getenv('AZURE_OPENAI_EMBEDDING_DEPLOYMENT','text-embedding-3-small')}")
    logger.info(f"AZURE_SEARCH_ENDPOINT : {os.getenv('AZURE_SEARCH_ENDPOINT')}")
    logger.info(f"AZURE_SEARCH_INDEX_NAME : {os.getenv('AZURE_SEARCH_INDEX_NAME')}")
    logger.info("="*60)



    #validate the required enviroment variable 
    required_var=[
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_OPENAI_API_VERSION",
        "AZURE_SEARCH_ENDPOINT",
        "AZURE_SEARCH_INDEX_NAME",
        "AZURE_SEARCH_API_KEY"
        
    ]
    missing_var=[var for var in required_var if not  os.getenv(var)]
    if missing_var:
        logger.error(f"Missing required variable {missing_var}")
        logger.error("check the env file and ensure all the var should be there")
        return
    


    #initialed the embedding model: turn the text into a vector

    try:
        logger.info("Initialing the azure openai embedding.......")
        embeddings=AzureOpenAIEmbeddings(
            azure_deployment=os.getenv('AZURE_OPENAI_EMBEDDING_DEPLOYMENT','text-embedding-3-small'),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01"),
        )

        logger.info('Emnedding model is initialized sucessful')
    except Exception as e:
        logger.error(f"failed to initialized embedding model: {str(e)}")
        logger.error("verify your Azure Openai deployment and endpoint")
        return

    #initialising the azure search

    try:
        logger.info("Initialing the azure AI Search vector store.......")
        index_name = os.getenv("AZURE_SEARCH_INDEX_NAME")
        embeddings=AzureSearch(
            azure_search_endpoint=os.getenv('AZURE_SEARCH_ENDPOINT'),
            azure_search_key=os.getenv("AZURE_SEARCH_API_KEY"),
            index_name=index_name,
            embedding_function=embeddings.embed_query

            
        )


        logger.info(f'vector store initialized for index ;{index_name}')
    except Exception as e:
        logger.error(f"failed to initialized azure search : {str(e)}")
        logger.error("verify your Azure search endpoint and api key and index name ")
        return

    # Find pdf file in data folder 
    pdf_files= glob.glob(os.path.join(data_folder,"*.pdf"))

    if not pdf_files:
        logger.warning(f"no pdf found in{data_folder}. please add file ")

    logger.info(f"Found{len(pdf_files)} PDFs to process : {[os.path.basename(f) for f in pdf_files]}")


    all_split=[]

    #process each pdf 
    #we will iterate all the pdf file that pass though pdf path
    for pdf_path in pdf_files:
        try:
            logger.info(f"Loading: {os.path.basename(pdf_path)}.........")
            loader=PyPDFLoader(pdf_path)
            raw_doc=loader.load()



            #chunking strategy
            #we create a chunks 
            text_splitter=RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
             
            )
            splits= text_splitter.split_documents(raw_doc)

            # it help the ai where to find the answer c
            for split in splits:
                split.metadata["source"]=os.path.basename(pdf_path)
            

            all_split.extend(splits)
            logger.info(f" split into {len(splits)} chunks.")
        except Exception as e:
            logger.error(f"failed to process {pdf_path}: {str(e)}")
        


        #upload all the split to the azure 
        if all_split:
            logger.info(f"uploading {len(all_split)} chunks to the azure AI search Index '{index_name}")

            try:

                #azure search accpet the chunk automatically via this method
                vector_store.add_documents(document=all_split)
                logger.info("="*60)
                logger.info("indexing complete! knowleadge base is ready")
                logger.info(f"total chunks indexed {len(all_split)}")
                logger.info("="*60) #print = 60 times

            except Exception as e:
                logger.error(f"failed to upload a document to azure search : {str(e)}")
                logger.error(f"please check the azure search configuration and try again")

        else:
            logger.warning("no document were processed ")

if __name__ == "__main__":
    index_doc()
        






        




