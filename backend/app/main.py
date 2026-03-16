"""
Main module for the Label Reader backend API.
"""
import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from ollama import Client

app = FastAPI(title="Label Reader API")

# Use environment variable for Ollama host,
# fallback to the dev instance from GEMINI.md
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "https://ollama.home.trprince.com")
ollama_client = Client(host=OLLAMA_HOST)


@app.post("/api/extract")
async def extract_label(file: UploadFile = File(...)):
    """
    Extracts structured data from an uploaded image of a label.
    """
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    contents = await file.read()

    # Process with ollama
    try:
        response = ollama_client.chat(
            model='qwen2.5-vl:7b',
            messages=[{
                'role': 'user',
                'content': 'Extract the text from this label.',
                'images': [contents]
            }]
        )
        return {"result": response['message']['content']}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
