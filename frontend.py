# =========================
# IMPORTS
# =========================
import streamlit as st
import requests
import markdown


API_BASE = "http://localhost:8000"


# -------------------------
# PAGE CONFIG
# -------------------------
st.set_page_config(page_title="AI Blog Writing Agent", layout="wide")


# -------------------------
# GLOBAL CSS (ONLY ONCE)
# -------------------------
def load_css():
    st.markdown("""
    <style>
    h1 {
        font-size: 40px;
        color: #1E88E5;
    }

    h2 {
        font-size: 30px;
        color: #1565C0;
        margin-top: 15px;
    }

    h3 {
        font-size: 22px;
        color: #0D47A1;
    }

    p {
        font-size: 18px;
        line-height: 1.8;
    }

    .block {
        background: #000000;
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0px 2px 12px rgba(0,0,0,0.08);
        margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)


load_css()

st.title("🧠 AI Blog Writing Agent")


# -------------------------
# SIDEBAR
# -------------------------
st.sidebar.header("⚙️ Controls")

topic = st.sidebar.text_input("Topic", "Artificial Intelligence")
tone = st.sidebar.selectbox("Tone", ["Professional", "Formal", "Technical"])
word_count = st.sidebar.number_input("Word Count", 100, 3000, 800)

option = st.sidebar.selectbox(
    "Choose Action",
    ["Upload PDF", "Search", "Planner", "Blog Generator", "Stream Writer"]
)


# -------------------------
# UPLOAD PDF
# -------------------------
if option == "Upload PDF":
    st.subheader("📄 Upload PDF")

    file = st.file_uploader("Select a file:", type=["pdf"])

    if file and st.button("Upload"):
        with st.spinner("uploading..."):
        
            files = {"file": (file.name, file, "application/pdf")}

            res = requests.post(f"{API_BASE}/upload", files=files)

            st.success("Uploaded Successfully")
            # st.json(res.json())


# -------------------------
# SEARCH
# -------------------------
elif option == "Search":
    st.subheader("🔎 Search Knowledge in Uploaded Document")
    st.text("Note: Please upload the document first to search.")

    query = st.text_input("Enter query")

    if st.button("Search"):
        res = requests.post(f"{API_BASE}/search", json={"query": query})

        st.markdown(f"""
        <div class="block">
        {res.json()["answer"]}
        </div>
        """, unsafe_allow_html=True)


# -------------------------
# PLANNER
# -------------------------
elif option == "Planner":
    st.subheader("🧩 Blog Planner")
    st.text("Note: This tool will generate the outlines for your Blog.")

    if st.button("Generate Outline"):
        res = requests.post(
            f"{API_BASE}/planner",
            json={
                "topic": topic,
                "tone": tone,
                "word_count": word_count,
            },
        )

        st.markdown(f"""
        <div class="block">
        {res.json()["outline"]}
        </div>
        """, unsafe_allow_html=True)


# -------------------------
# BLOG GENERATOR
# -------------------------
elif option == "Blog Generator":
    st.subheader("🚀 Complete Blog Generator")

    if st.button("Generate Blog"):

        with st.spinner("Generating blog with image..."):

            response = requests.post(
                f"{API_BASE}/graph",
                json={
                    "topic": topic,
                    "tone": tone,
                    "word_count": word_count,
                },
            )

        if response.status_code == 200:

            result = response.json()

            blog = result["final_blog"]
            image_prompt = result.get("image_prompt", "")
            image_url = result.get("image_url", "")

            # Convert Markdown → HTML
            html = markdown.markdown(blog)

            # Show Blog
            st.markdown(f"""
            <div class="block">
            {html}
            </div>
            """, unsafe_allow_html=True)

            # Show Image Prompt (Optional)
            if image_prompt:
                with st.expander("📝 Image Prompt"):
                    st.write(image_prompt)

            # Show Generated Image
            if image_url:
                st.subheader("🖼 Featured Image")
                st.image(image_url, use_container_width=True)

        else:
            st.error("Failed to generate blog.")


# -------------------------
# STREAM WRITER (REAL TIME)
# -------------------------
elif option == "Stream Writer":
    st.subheader("⚡ Live Streaming Blog Writer")

    if st.button("Start Streaming"):

        placeholder = st.empty()
        full_text = ""

        response = requests.post(
            f"{API_BASE}/stream-writer",
            json={
                "topic": topic,
                "tone": tone,
                "word_count": word_count,
            },
            stream=True,
        )

        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                full_text += chunk.decode("utf-8")

                placeholder.markdown(f"""
                <div class="block">
                {full_text}
                </div>
                """, unsafe_allow_html=True)