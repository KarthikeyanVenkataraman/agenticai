# create_sop_index.py

from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from dotenv import load_dotenv
import os

# ✅ Load .env from the correct path
env_path = os.path.join(os.getcwd(), ".env")
load_dotenv(dotenv_path=env_path)

# ✅ Confirm OpenAI key is loaded
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found. Check your .env path.")

print(f"✅ OpenAI key loaded: {api_key[:8]}...")

# ✅ 1. Load your PDF
pdf_path = os.path.join("sop", "ONBOARDING_SOP.pdf")
loader = PyPDFLoader(pdf_path)
documents = loader.load()

print(f"✅ Loaded {len(documents)} page(s)")

# ✅ 2. Chunk the text
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)
chunks = splitter.split_documents(documents)

print(f"✅ Split into {len(chunks)} chunks")

# ✅ 3. Create embeddings
embeddings = OpenAIEmbeddings()

# ✅ 4. Create & persist Chroma vector DB
vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory="sop_chroma_db"
)

vectorstore.persist()

print("✅ Vector store created at 'sop_chroma_db'")
