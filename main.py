from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from embedder import compare

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Docs(BaseModel):
    doc1: str
    doc2: str

@app.post("/compare")
def compare_docs(docs: Docs):
    return compare(docs.doc1, docs.doc2)
