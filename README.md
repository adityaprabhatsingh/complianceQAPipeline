# Brand Guardian AI: Multimodal Compliance Orchestration Engine


## 📖 Description
Brand Guardian AI is an end-to-end, production-grade LLMOps project designed to automate the auditing of video advertisements against strict legal frameworks (e.g., FTC guidelines) and platform specifications (e.g., YouTube Ad Specs).
<img width="1063" height="562" alt="Screenshot 2026-07-24 at 3 56 06 PM" src="https://github.com/user-attachments/assets/23cbf07b-7f4c-4f81-a817-bc637e4950e5" />

Instead of relying on manual reviews, this system ingests a YouTube URL, extracts multimodal data (OCR, audio transcripts, metadata), retrieves relevant compliance rules via a RAG pipeline, and orchestrates an AI agent to determine if the video passes or fails compliance—complete with detailed, severity-flagged reporting.

## 🏗️ System Architecture
The pipeline is orchestrated using LangGraph, passing data seamlessly between the ingestion services, the RAG knowledge base, and the compliance auditor agent.
<img width="1600" height="842" alt="WhatsApp Image 2026-06-09 at 11 55 52" src="https://github.com/user-attachments/assets/7167b496-036b-4eb6-89d2-16fc3292b79f" />


## 📊 Observability & Monitoring
To ensure production readiness, the system integrates OpenTelemetry to track latency, API limits, and system health. The telemetry data is pushed to Azure Application Insights.

The telemetry map demonstrates live tracking of API calls between the FastAPI server, Azure Video Indexer, YouTube CDN, and LangSmith.

<img width="1600" height="931" alt="WhatsApp Image 2026-06-09 at 11 55 52 (1)" src="https://github.com/user-attachments/assets/3b4d33f5-863b-477c-850f-8fe842374fcf" />



 
## 📸 Demo / Screenshot
<img width="1600" height="738" alt="fastapiswagger" src="https://github.com/user-attachments/assets/dd06adf3-8c75-4cfc-9154-ff4b2f268f2c" />




## ✨ Features
Automated Video Ingestion: Downloads YouTube videos directly using yt-dlp and stages them in Azure Blob Storage.

Multimodal Extraction: Leverages Azure Video Indexer to extract on-screen text (OCR) and spoken dialogue (transcripts).

Agentic Orchestration: Uses a stateful LangGraph workflow to pass data seamlessly between the indexer nodes and the auditor nodes.

Intelligent Rule Retrieval (RAG): Embeds and queries complex legal PDF documents stored in an Azure AI Search vector database.

Robust Observability: Complete tracing, latency monitoring, and logging implemented via LangSmith and Azure Application Insights (OpenTelemetry).

Production-Ready API: Served via a high-performance FastAPI backend.


##<img width="1022" height="330" alt="Screenshot 2026-07-24 at 3 57 04 PM" src="https://github.com/user-attachments/assets/165ed49c-978e-4daf-afd2-57d7416459b6" />

## 🛠️ Tech Stack
### Language/Package Manager: Python, uv

### Frameworks: FastAPI, LangChain, LangGraph

### AI & Machine Learning: Azure OpenAI (GPT-4o, Text-Embedding-3-Small)

### Cloud Infrastructure (Azure): Azure Blob Storage, Azure Video Indexer, Azure AI Search

### Observability: LangSmith, Azure Application Insights

### Tools: yt-dlp, Pydantic



## 🚀 Getting Started
Prerequisites
Python 3.10+

uv package manager installed

An active Azure account with the necessary services deployed (OpenAI Foundry, AI Search, Blob Storage, Video Indexer, App Insights).

Node.js (required by yt-dlp for certain extractions).

## 🤝 Contributing
​This project is open source. Contributions, issues, and feature requests are welcome!

​### 1. Fork the Project

​### 2. Create your Feature Branch 
(
git checkout -b feature/AmazingFeature
)


​### 3. Commit your Changes 
(
git commit -m 'Add some AmazingFeature'
)


​### 4. Push to the Branch 
(
git push origin feature/AmazingFeature
)


​5. Open a Pull Request

## Installation


<img width="1012" height="532" alt="Screenshot 2026-07-24 at 3 56 43 PM" src="https://github.com/user-attachments/assets/ff475524-400c-4d63-993f-0ecbfe625b8d" />

## 1. Clone the repository:

   git clone https://github.com/adityaprabhatsingh/complianceQAPipeline.git
   cd complianceQAPipeline
   
##2. Initialize the environment using uv:
   uv sync

## 3.Congigure Environment Variable 
   Add a all the congiguration after gernating from required webpage 


 4. Index the Compliance Documents

  Place your rulebook PDFs in the ( backend/data ) folder, then run the indexing script to populate your vector database

### Usage
  start the FastAPI backend server:
  (
  uv run uvicorn backend.src.api.server:app --reload
  )

  once running, navigate to 
  http://localhost:8000/docs
  to interact with API via the Swagger UI
  

  

