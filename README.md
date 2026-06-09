# Brand Guardian AI: Multimodal Compliance Orchestration Engine


##📖 Description
Brand Guardian AI is an end-to-end, production-grade LLMOps project designed to automate the auditing of video advertisements against strict legal frameworks (e.g., FTC guidelines) and platform specifications (e.g., YouTube Ad Specs).

Instead of relying on manual reviews, this system ingests a YouTube URL, extracts multimodal data (OCR, audio transcripts, metadata), retrieves relevant compliance rules via a RAG pipeline, and orchestrates an AI agent to determine if the video passes or fails compliance—complete with detailed, severity-flagged reporting.

##📸 Demo / Screenshot
<img width="1600" height="738" alt="fastapiswagger" src="https://github.com/user-attachments/assets/dd06adf3-8c75-4cfc-9154-ff4b2f268f2c" />




## ✨ Features
Automated Video Ingestion: Downloads YouTube videos directly using yt-dlp and stages them in Azure Blob Storage.

Multimodal Extraction: Leverages Azure Video Indexer to extract on-screen text (OCR) and spoken dialogue (transcripts).

Agentic Orchestration: Uses a stateful LangGraph workflow to pass data seamlessly between the indexer nodes and the auditor nodes.

Intelligent Rule Retrieval (RAG): Embeds and queries complex legal PDF documents stored in an Azure AI Search vector database.

Robust Observability: Complete tracing, latency monitoring, and logging implemented via LangSmith and Azure Application Insights (OpenTelemetry).

Production-Ready API: Served via a high-performance FastAPI backend.



## 🛠️ Tech Stack
Language/Package Manager: Python, uv

Frameworks: FastAPI, LangChain, LangGraph

AI & Machine Learning: Azure OpenAI (GPT-4o, Text-Embedding-3-Small)

Cloud Infrastructure (Azure): Azure Blob Storage, Azure Video Indexer, Azure AI Search

Observability: LangSmith, Azure Application Insights

Tools: yt-dlp, Pydantic



## 🚀 Getting Started
Prerequisites
Python 3.10+

uv package manager installed

An active Azure account with the necessary services deployed (OpenAI Foundry, AI Search, Blob Storage, Video Indexer, App Insights).

Node.js (required by yt-dlp for certain extractions).

## 🤝 Contributing
​This project is open source. Contributions, issues, and feature requests are welcome!

​1. Fork the Project

​2. Create your Feature Branch 
(
git checkout -b feature/AmazingFeature
)


​3. Commit your Changes 
(
git commit -m 'Add some AmazingFeature'
)


​4. Push to the Branch 
(
git push origin feature/AmazingFeature
)


​5. Open a Pull Request

