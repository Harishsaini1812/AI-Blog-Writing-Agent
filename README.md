# 🧠 AI Blog Writing Agent (Multi-Agent System)

An advanced AI-powered blog generation system built using LangGraph, FastAPI, Streamlit, and OpenAI APIs. This project demonstrates a complete multi-agent architecture where different AI agents collaborate to plan, research, write, review, and generate images for blogs.

---

## 🚀 Features

- 🧩 Multi-Agent System using LangGraph
  - Planner Agent → Creates structured blog outline
  - Research Agent → Fetches web + PDF knowledge
  - Writer Agent → Generates high-quality blog content
  - Reviewer Agent → Improves SEO, grammar, readability
  - Image Prompt Agent → Generates image prompt
  - Image Generator Agent → Creates featured blog image

- 🌐 Real-time Web Search using Tavily API
- 📚 Retrieval-Augmented Generation (RAG) using FAISS
- 🧠 PDF-based knowledge base support
- ⚡ Streaming blog generation (real-time output)
- 🖼 AI-generated featured blog images (OpenAI GPT-image-1)
- 📄 PDF upload and processing system
- 🔎 Semantic search over documents
- 🎨 Streamlit-based interactive frontend
- 🐳 Docker-ready architecture (optional)
- ☁️ Deployable on AWS EC2

---

## 🏗️ Tech Stack

- Backend: FastAPI
- Frontend: Streamlit
- AI Models: OpenAI GPT-4.1-mini, GPT-image-1
- Frameworks: LangGraph, LangChain
- Search API: Tavily
- Vector Database: FAISS
- Embeddings: text-embedding-3-small
- PDF Processing: PyPDFLoader
- Deployment: Docker, AWS EC2

---

## 📂 Project Structure

AI-Blog-Agent/
│
├── backend.py              # FastAPI + LangGraph workflow
├── frontend.py             # Streamlit UI
├── requirements.txt
├── .env                    # API keys (not committed)
│
├── data/                   # Uploaded PDFs
├── faiss_index/            # Vector database storage
├── temp/                   # Generated images
│
└── README.md

---

## ⚙️ Installation

### 1. Clone Repository
git clone https://github.com/your-username/ai-blog-agent.git
cd ai-blog-agent

---

### 2. Create Virtual Environment
python -m venv env

# Windows
env\Scripts\activate

# Mac/Linux
source env/bin/activate

---

### 3. Install Dependencies
pip install -r requirements.txt

---

### 4. Setup Environment Variables

Create a `.env` file and add:

OPENAI_API_KEY=your_openai_api_key
TAVILY_API_KEY=your_tavily_api_key
GOOGLE_API_KEY=your_google_api_key

---

## ▶️ Run Project

### Start Backend (FastAPI)
uvicorn backend:app --reload

---

### Start Frontend (Streamlit)
streamlit run frontend.py

---

## 🧠 How It Works

1. User enters topic in Streamlit UI  
2. Planner Agent creates blog outline  
3. Research Agent gathers web + PDF context  
4. Writer Agent generates blog content  
5. Reviewer Agent improves final blog  
6. Image Prompt Agent generates prompt  
7. Image Generator Agent creates featured image  
8. Final blog + image shown in UI  

---

## 📌 API Endpoints

- POST /upload → Upload PDF
- POST /search → Ask questions from documents (RAG)
- POST /planner → Generate blog outline
- POST /graph → Full blog generation pipeline
- POST /stream-writer → Streaming blog generation

---

## 🖼 Output Example

- SEO optimized blog
- Markdown formatted content
- AI generated featured image
- Real-time streaming writing experience

---

## 🔥 Key Highlights

- Multi-agent AI architecture
- Real-time streaming output
- Hybrid knowledge system (Web + PDF RAG)
- Production-style FastAPI backend
- Clean Streamlit frontend integration

---

## 📈 Future Improvements

- Download blog as PDF
- User authentication system
- Database integration (MongoDB/PostgreSQL)
- Blog history dashboard
- Cloud deployment (AWS + CI/CD)
- Multi-language blog generation

---

## 👨‍💻 Author

Harish Kumar Saini

---

## ⭐ Support

If you like this project, please give it a star ⭐ on GitHub.
