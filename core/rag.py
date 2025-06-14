import os
import json
import markdown2
from typing import List
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage,
    Settings,
)
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.schema import Document
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.prompts import PromptTemplate

load_dotenv()

# ==== CONFIGURATION ====
MARKDOWN_DIR = "data/downloaded_md_files"  # directory containing .md files
DISCOURSE_JSON_PATH = "data/discourse.json"
INDEX_PERSIST_DIR = "data/storage"

# ==== TEXT CLEANING ====


def clean_markdown(md_text: str) -> str:
    html = markdown2.markdown(md_text)
    return BeautifulSoup(html, "html.parser").get_text(separator=" ").strip()


def clean_html(html_text: str) -> str:
    return BeautifulSoup(html_text, "html.parser").get_text(separator=" ").strip()


# ==== SETUP LLAMAINDEX SETTINGS ====
def configure_llamaindex():
    Settings.llm = OpenAI(model="gpt-3.5-turbo", temperature=0)
    Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")
    Settings.node_parser = SentenceSplitter(chunk_size=500, chunk_overlap=80)


# ==== LOAD DOCUMENTS ====
def load_markdown_docs() -> List[Document]:
    return [
        Document(text=clean_markdown(doc.text), metadata=doc.metadata)
        for doc in SimpleDirectoryReader(MARKDOWN_DIR).load_data()
    ]


def load_discourse_docs() -> List[Document]:
    with open(DISCOURSE_JSON_PATH, "r") as f:
        discourse_posts = json.load(f)
    return [
        Document(text=clean_html(post["content"]), metadata={"source": post["source"]})
        for post in discourse_posts
    ]


def load_all_documents() -> List[Document]:
    md_docs = load_markdown_docs()
    disc_docs = load_discourse_docs()
    return md_docs + disc_docs


# ==== BUILD OR LOAD VECTOR INDEX ====
def get_or_build_index() -> VectorStoreIndex:
    if os.path.exists(INDEX_PERSIST_DIR):
        print("Loading index from disk...")
        storage_context = StorageContext.from_defaults(persist_dir=INDEX_PERSIST_DIR)
        return load_index_from_storage(storage_context)
    else:
        print("Building new index and persisting to disk...")
        documents = load_all_documents()
        index = VectorStoreIndex.from_documents(documents)
        index.storage_context.persist(persist_dir=INDEX_PERSIST_DIR)
        return index


# ==== CUSTOM PROMPT QUERY ENGINE ====
custom_json_prompt = PromptTemplate(
    """
    Given the context and any extracted text from an image, answer the user's question.

    ---

    **Instructions:**

    1.  **Identify the Question:** Locate the user's primary question and any relevant text extracted from an image at the end of the input.
    2.  **Formulate Response:**
        * **Strictly base your answer ONLY on the provided Context and Text Extracted From Image.**
        * If **Text Extracted From Image** is present, incorporate relevant information from it into your answer.
    3.  **Handle Unanswerable Questions (Strictly):** If the question cannot be answered **directly and completely** using **only** the provided **Context** and **Text Extracted From Image**, then state clearly: "I cannot answer this question with the available data." Do not infer, speculate, or use external knowledge.
    4.  AND DON'T FORGET TO ADD SOURCE URLS FROM THE CONTEXT 
    5.  **Format Output:** Your response **must** be in the following strict JSON format:

    
    {
      "answer": "<your full answer>",
      "links": [
        {"url": "<source url 1>", "text": "<short note or snippet>"},
        {"url": "<source url 2>", "text": "<short note or snippet>"},
        ...
      ]
    }
    

    ---

    **Context:**
    {context_str}

    **Question:** {query_str}
    """
)


intelligence_prompt = PromptTemplate(
    """
    Given the context and any extracted text from an image, answer the user's question.

    ---

    **Instructions:**

    1.  **Identify the Question:** Locate the user's primary question and any relevant text extracted from an image at the end of the input.
    2.  **Formulate Response:** Prioritize Solving the **Text Extracted from Image** part then the Context
    4.  AND DON'T FORGET TO ADD SOURCE URLS FROM THE CONTEXT 
    5.  **Format Output:** Your response **must** be in the following strict JSON format:

    
    {
      "answer": "<your full answer>",
      "links": [
        {"url": "<source url 1>", "text": "<short note or snippet>"},
        {"url": "<source url 2>", "text": "<short note or snippet>"},
        ...
      ]
    }
    

    ---

    **Context:**
    {context_str}

    **Question:** {query_str}
"""
)


def query_index(index: VectorStoreIndex, query: str, intelligence: bool, top_k: int = 5) -> str:
    retriever = index.as_retriever(similarity_top_k=top_k)

    if intelligence == True:
        query_engine = RetrieverQueryEngine.from_args(
            retriever=retriever, text_qa_template=intelligence_prompt
        )
        return str(query_engine.query(query))
    else:
        query_engine = RetrieverQueryEngine.from_args(
            retriever=retriever, text_qa_template=custom_json_prompt
        )
        return str(query_engine.query(query))


# ==== EXAMPLE USAGE ====
# if __name__ == "__main__":
#     print("Setting up RAG pipeline...")
#     configure_llamaindex()
#     index = get_or_build_index()
#     response = query_index(index, "Which OpenAI model should be used in GA5 Q8?")
#     print("\nAnswer:\n", response)
