import streamlit as st
import requests
import base64
import json

st.set_page_config(page_title="RAG QA System", layout="centered")

st.title("🧠 RAG Virtual Assistant")

# Form input
with st.form("query_form"):
    question = st.text_area("📋 Enter your question:", max_chars=1000)
    image_file = st.file_uploader("🖼️ (Optional) Upload image", type=["png", "jpg", "jpeg", "webp"])
    submit = st.form_submit_button("Ask")

if submit:
    if not question.strip():
        st.warning("Please enter a question.")
    else:
        # Prepare request
        payload = {"question": question, "image": None}

        if image_file:
            image_bytes = image_file.read()
            payload["image"] = base64.b64encode(image_bytes).decode("utf-8")

        try:
            with st.spinner("🧠 Thinking..."):
                res = requests.post("http://localhost:8000/api", json=payload)
                if res.status_code == 200:
                    answer = res.json()
                    st.success("✅ Answer:")
                    st.write(answer)
                else:
                    st.error(f"❌ Error {res.status_code}: {res.text}")
        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to FastAPI backend. Make sure it's running on http://localhost:8000.")
