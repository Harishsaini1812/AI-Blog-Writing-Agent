# =========================
# IMPORTS
# =========================
import os
import requests
import uuid
import base64
import shutil
import json
from typing import TypedDict

from dotenv import load_dotenv

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from openai import OpenAI
from tavily import TavilyClient

from google import genai

from langgraph.graph import StateGraph, START, END

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


# =========================================================
# ENVIRONMENT VARIABLES
# =========================================================
# Load API keys from .env file (NEVER hardcode in production)
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# Safety check to avoid silent failures
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is missing")

if not TAVILY_API_KEY:
    raise ValueError("TAVILY_API_KEY is missing")


# =========================================================
# CLIENT INITIALIZATION
# =========================================================
# OpenAI client for LLM + image generation
client = OpenAI(api_key=OPENAI_API_KEY)

# Tavily client for web search (real-time research)
tavily_client = TavilyClient(api_key=TAVILY_API_KEY)

# Embeddings model for RAG (vector search)
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    api_key=OPENAI_API_KEY
)

# Google GenAI client (currently not heavily used in flow)
google_client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))


# =========================
# FASTAPI APP
# =========================
# Main backend service for AI blog generation pipeline
app = FastAPI(title="AI Blog Writing Agent")


# =========================================================
# DIRECTORY SETUP
# =========================================================
# Ensure required folders exist before runtime
os.makedirs("data", exist_ok=True)         # uploaded PDFs
os.makedirs("faiss_index", exist_ok=True)  # vector DB storage
os.makedirs("temp", exist_ok=True)         # generated images

# Serve generated images publicly via FastAPI
app.mount("/images", StaticFiles(directory="temp"), name="images")


# =========================================================
# REQUEST SCHEMAS
# =========================================================
class SearchRequest(BaseModel):
    query: str


class PlannerRequest(BaseModel):
    topic: str
    tone: str
    word_count: int


# =========================================================
# STATE DEFINITION (LangGraph memory structure)
# =========================================================
class BlogState(TypedDict):
    topic: str
    tone: str
    word_count: int

    outline: str
    web_research: str
    rag_context: str

    draft: str
    final_blog: str

    image_prompt: str
    image_url: str


# =========================================================
# HEALTH CHECK ENDPOINT
# =========================================================
@app.get("/")
def home():
    return {"message": "AI Blog Writing Agent Running 🚀"}


# =========================================================
# PDF PROCESSING PIPELINE (RAG SETUP)
# =========================================================
def process_pdf(file_path: str):
    # Load PDF into documents
    loader = PyPDFLoader(file_path)
    documents = loader.load()

    # Split into chunks for embeddings
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    return splitter.split_documents(documents)


def create_vector_store(documents):
    # Create or update FAISS vector database
    if os.path.exists("faiss_index"):
        db = FAISS.load_local(
            "faiss_index",
            embeddings,
            allow_dangerous_deserialization=True
        )
        db.add_documents(documents)
    else:
        db = FAISS.from_documents(documents, embeddings)

    db.save_local("faiss_index")
    return db


def retrieve_context(query: str, k: int = 5):
    # Retrieve relevant context from FAISS
    if not os.path.exists("faiss_index"):
        return ""

    db = FAISS.load_local(
        "faiss_index",
        embeddings,
        allow_dangerous_deserialization=True
    )

    docs = db.similarity_search(query, k=k)

    return "\n\n".join([d.page_content for d in docs])


# =========================================================
# LLM HELPER FUNCTION
# =========================================================
def llm(system_prompt: str, user_prompt: str, temperature: float = 0.7):
    # Wrapper for OpenAI chat completion API
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        temperature=temperature,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )

    return response.choices[0].message.content


# =========================================================
# WEB SEARCH TOOL (TAVILY)
# =========================================================
def web_search(query: str):
    # Fetch real-time web data for blog enhancement
    response = tavily_client.search(
        query=query,
        search_depth="advanced",
        max_results=5
    )

    results = []

    for item in response["results"]:
        results.append(
            f"""
Title: {item['title']}
Content: {item['content']}
URL: {item['url']}
"""
        )

    return "\n\n".join(results)


# =========================================================
# LANGGRAPH AGENTS
# =========================================================

# -------------------------
# 1. BLOG PLANNER AGENT
# -------------------------
def planner_agent(state: BlogState):
    # Creates structured SEO outline
    system_prompt = """
    You are an expert SEO blog planner.
    Create structured blog outlines.
    """

    user_prompt = f"""
    Topic: {state['topic']}
    Tone: {state['tone']}
    Word Count: {state['word_count']}

    Return:
    - Title
    - Audience
    - Keywords
    - Outline
    """

    outline = llm(system_prompt, user_prompt, temperature=0.3)

    return {**state, "outline": outline}


# -------------------------
# 2. RESEARCH AGENT (RAG + WEB)
# -------------------------
def research_agent(state: BlogState):
    web_results = web_search(state["topic"])
    rag_context = retrieve_context(state["topic"])

    return {
        **state,
        "web_research": web_results,
        "rag_context": rag_context
    }


# -------------------------
# 3. WRITER AGENT
# -------------------------
def writer_agent(state: BlogState):
    system_prompt = """
    You are an expert SEO blog writer.
    Write high quality Markdown blogs.
    """

    user_prompt = f"""
    Topic: {state['topic']}

    Outline:
    {state['outline']}

    Web Research:
    {state['web_research']}

    RAG Context:
    {state['rag_context']}

    Word Count: {state['word_count']}
    """

    blog = llm(system_prompt, user_prompt, temperature=0.8)

    return {**state, "draft": blog}


# -------------------------
# 4. REVIEWER / EDITOR AGENT
# -------------------------
def reviewer_agent(state: BlogState):
    system_prompt = """
    You are an expert blog editor and SEO reviewer.
    Improve grammar, readability, SEO, and formatting.
    """

    user_prompt = f"""
    Here is the blog draft:

    {state['draft']}
    """

    final_blog = llm(system_prompt, user_prompt, temperature=0.3)

    return {"final_blog": final_blog}


# -------------------------
# 5. IMAGE PROMPT AGENT
# -------------------------
def image_prompt_agent(state: BlogState):
    # Converts blog into image generation prompt
    system_prompt = """
    You are an AI image prompt engineer.
    Generate ONE high-quality image prompt.
    Return ONLY prompt text.
    """

    user_prompt = f"""
    Blog:
    {state["final_blog"]}
    """

    prompt = llm(system_prompt, user_prompt, temperature=0.3)

    return {**state, "image_prompt": prompt}


# -------------------------
# 6. IMAGE GENERATION AGENT
# -------------------------
def image_generator_agent(state):
    print("🔥 IMAGE GENERATION STARTED")

    # OpenAI image generation API call
    response = client.images.generate(
        model="gpt-image-1",
        prompt=state["image_prompt"],
        size="1024x1024"
    )

    # Safety check: ensure image exists
    if not response.data:
        raise ValueError("No image returned from API")

    image_data = response.data[0]

    image_path = f"temp/{uuid.uuid4()}.png"

    # Case 1: URL-based image
    if hasattr(image_data, "url") and image_data.url:
        img = requests.get(image_data.url).content

    # Case 2: Base64-based image (most common)
    elif hasattr(image_data, "b64_json"):
        img = base64.b64decode(image_data.b64_json)

    else:
        raise ValueError("Unknown image format returned by API")

    # Save image locally
    with open(image_path, "wb") as f:
        f.write(img)

    return {
        **state,
        "image_url": f"http://127.0.0.1:8000/images/{os.path.basename(image_path)}"
    }


# =========================================================
# LANGGRAPH FLOW HELPERS
# =========================================================
def stream_graph(state: BlogState):
    result = graph.invoke(state)

    final_output = result["final_blog"] or result["draft"]

    for chunk in final_output.split("\n"):
        yield json.dumps({"chunk": chunk}) + "\n"


def stream_writer(state: BlogState):
    # Streaming blog writer (real-time output)
    system_prompt = """
    IMPORTANT: return clean markdown only
    """

    user_prompt = f"""
    Topic: {state['topic']}
    """

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        stream=True
    )

    for chunk in response:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content


# =========================================================
# GENERATE ANSWER FOR SEARCH ENGINE
# =========================================================
def answer_from_rag(query: str):
    # Step 1: Retrieve relevant context from FAISS vector database
    # This uses semantic search to find top matching chunks from uploaded PDFs
    context = retrieve_context(query)

    # Step 2: System prompt defines strict behavior of the AI tutor
    # - Only use provided context
    # - Do not hallucinate outside information
    # - If context is insufficient, explicitly say "I don't know"
    system_prompt = """
    You are an AI tutor.

    Answer ONLY using the provided context.
    If the answer is not present, say you don't know.

    Give a concise, well-formatted explanation.
    """

    # Step 3: User prompt combines retrieved context + user question
    # This is what LLM will actually use to generate response
    user_prompt = f"""
    Context:
    {context}

    Question:
    {query}
    """

    # Step 4: Call LLM with temperature=0 for deterministic, factual output
    # Lower temperature ensures strict grounding in context
    return llm(system_prompt, user_prompt, temperature=0)



# =========================
# LANGGRAPH PIPELINE
# =========================
builder = StateGraph(BlogState)

builder.add_node("planner", planner_agent)
builder.add_node("research", research_agent)
builder.add_node("writer", writer_agent)
builder.add_node("reviewer", reviewer_agent)
builder.add_node("image_prompt", image_prompt_agent)
builder.add_node("image_gen", image_generator_agent)

builder.add_edge(START, "planner")
builder.add_edge("planner", "research")
builder.add_edge("research", "writer")
builder.add_edge("writer", "reviewer")
builder.add_edge("reviewer", "image_prompt")
builder.add_edge("image_prompt", "image_gen")
builder.add_edge("image_gen", END)

graph = builder.compile()


# =================================================
# API ENDPOINTS - AI BLOG GENERATION SYSTEM
# =================================================
@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):

    file_path = os.path.join("data", file.filename)

    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    docs = process_pdf(file_path)
    create_vector_store(docs)

    return {
        "status": "success",
        "file": file.filename,
        "chunks": len(docs)
    }


@app.post("/search")
def search(request: SearchRequest):

    answer = answer_from_rag(request.query)

    return {
        "query": request.query,
        "answer": answer
    }


@app.post("/planner")
def planner(request: PlannerRequest):

    state = BlogState(
        topic=request.topic,
        tone=request.tone,
        word_count=request.word_count,
        outline="",
        web_research="",
        rag_context="",
        draft="",
        final_blog="",
        image_prompt="",
        image_url=""
    )

    result = planner_agent(state)

    return result


@app.post("/research")
def research(request: PlannerRequest):

    state = BlogState(
        topic=request.topic,
        tone=request.tone,
        word_count=request.word_count,
        outline="",
        web_research="",
        rag_context="",
        draft="",
        final_blog="",
        image_prompt="",
        image_url=""
    )

    return research_agent(state)


@app.post("/graph")
def run_graph(request: PlannerRequest):

    state = BlogState(
        topic=request.topic,
        tone=request.tone,
        word_count=request.word_count,
        outline="",
        web_research="",
        rag_context="",
        draft="",
        final_blog="",
        image_prompt="",
        image_url=""
    )

    result = graph.invoke(state)

    return {
    "outline": result["outline"],
    "draft": result["draft"],
    "final_blog": result["final_blog"],
    "image_prompt": result["image_prompt"],
    "image_url": result["image_url"]
}


@app.post("/stream")
def stream_blog(request: PlannerRequest):

    state = BlogState(
        topic=request.topic,
        tone=request.tone,
        word_count=request.word_count,

        outline="",
        web_research="",
        rag_context="",

        draft="",
        final_blog="",

        image_prompt="",
        image_url=""
    )

    return StreamingResponse(
        stream_graph(state),
        media_type="application/json"
    )


@app.post("/stream-writer")
def stream_writer_api(request: PlannerRequest):

    state = {
        "topic": request.topic,
        "tone": request.tone,
        "word_count": request.word_count,
        "outline": "",
        "web_research": "",
        "rag_context": "",
        "draft": "",
        "final_blog": "",
        "image_prompt": "",
        "image_url": ""
    }

    state = planner_agent(state)
    state = research_agent(state)

    return StreamingResponse(
        stream_writer(state),
        media_type="text/plain"
    )

