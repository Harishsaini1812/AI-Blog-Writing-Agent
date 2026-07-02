🚀 AI Blog Writing Agent

An end-to-end multi-agent AI content generation system that automatically creates high-quality blog posts using LLMs, RAG, web search, and AI image generation. The system is built using a modular agentic architecture powered by LangGraph and exposed via FastAPI + Streamlit UI.

📌 Overview

This project automates the entire blog creation workflow:

Topic planning
Web research
Knowledge retrieval (RAG)
Blog writing
Content review & optimization
AI image generation
Real-time streaming output

It behaves like an autonomous AI writing assistant capable of producing SEO-optimized blogs with contextual accuracy.

✨ Features
🤖 Multi-Agent System (LangGraph)
Planner Agent
Research Agent
Writer Agent
Reviewer Agent
Image Generator Agent
🌐 Real-Time Web Search Integration
Uses Tavily API for up-to-date information
📚 Retrieval-Augmented Generation (RAG)
FAISS-based vector database for document retrieval
PDF ingestion and semantic search
🧠 LLM-Powered Content Creation
OpenAI GPT models for blog generation and refinement
🖼 AI Image Generation
Automatically generates featured blog images
⚡ Streaming Output
Real-time blog generation using FastAPI streaming
🖥 Interactive Frontend
Streamlit-based UI for seamless user interaction
🏗 Architecture
User Input (Topic)
        ↓
   Planner Agent
        ↓
  Research Agent (Web + RAG)
        ↓
   Writer Agent (Blog Draft)
        ↓
  Reviewer Agent (SEO + Polish)
        ↓
 Image Prompt Agent
        ↓
 Image Generator Agent
        ↓
 Final Blog Output
🛠 Tech Stack
Backend: FastAPI
Frontend: Streamlit
LLMs: OpenAI GPT models
Agent Framework: LangGraph
RAG Pipeline: LangChain + FAISS
Web Search: Tavily API
Embeddings: OpenAI Embeddings
Image Generation: OpenAI / Gemini API
Deployment: Docker, AWS EC2
📂 Project Structure
ai-blog-writing-agent/
│
├── backend.py              # FastAPI backend + LangGraph agents
├── frontend.py             # Streamlit UI
├── data/                   # Uploaded PDFs
├── temp/                   # Generated images
├── faiss_index/            # Vector DB
├── requirements.txt
├── .env.example
└── README.md
⚙️ Installation & Setup
1. Clone Repository
git clone https://github.com/your-username/ai-blog-writing-agent.git
cd ai-blog-writing-agent
2. Create Virtual Environment
python -m venv env
source env/bin/activate   # Linux/Mac
env\Scripts\activate      # Windows
3. Install Dependencies
pip install -r requirements.txt
4. Setup Environment Variables

Create a .env file:

OPENAI_API_KEY=your_openai_api_key
TAVILY_API_KEY=your_tavily_api_key
GOOGLE_API_KEY=your_google_api_key
5. Run Backend (FastAPI)
uvicorn backend:app --reload
6. Run Frontend (Streamlit)
streamlit run frontend.py
📊 Key Highlights
End-to-end autonomous content generation system
Modular agent-based architecture using LangGraph
Real-time streaming responses
Context-aware RAG system using FAISS
Integrated web search + generative AI pipeline
🧠 Future Improvements
📄 PDF export of generated blogs
🔗 Direct publishing to Medium / WordPress
📊 SEO scoring system
🧾 Multi-language blog generation
🎙 Voice-based input/output system
☁ Cloud deployment with CI/CD pipeline
📸 Screenshots

Add your Streamlit UI screenshots here

👨‍💻 Author

Harish Kumar Saini

⭐ Show Your Support

If you like this project, consider giving it a ⭐ on GitHub!
