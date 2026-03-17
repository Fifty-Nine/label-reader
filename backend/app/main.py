"""
Main module for the Label Reader backend API.
"""
import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from ollama import Client

app = FastAPI(title="Label Reader API")

# Use environment variable for Ollama host,
# fallback to the dev instance from GEMINI.md
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "https://ollama.home.trprince.com")
ollama_client = Client(host=OLLAMA_HOST)

# Configuration for static files (frontend)
STATIC_DIR = os.getenv("STATIC_DIR", "static")


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
            model='qwen3.5:9b',
            messages=[{
                'role': 'user',
                'content': 'Extract the text from this label.',
                'images': [contents]
            }]
        )
        return {"result": response['message']['content']}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


# SPA Fallback and Static File Serving
# These must be added AFTER the API routes to avoid overshadowing them.
if os.path.exists(STATIC_DIR):
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """
        Serves static files and provides a fallback for SPA routing.
        """
        # Exclude /api routes from being caught here (just in case)
        if full_path.startswith("api"):
            raise HTTPException(status_code=404, detail="API route not found")

        # Check if the requested file exists in the static directory
        file_path = os.path.join(STATIC_DIR, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)

        # Fallback to index.html for SPA routing (e.g. /about)
        index_path = os.path.join(STATIC_DIR, "index.html")
        if os.path.isfile(index_path):
            return FileResponse(index_path)

        raise HTTPException(status_code=404, detail="File not found")
else:
    # If static dir doesn't exist (e.g. during dev without built frontend)
    @app.get("/")
    async def root():
        """
        Root endpoint fallback when frontend is not built.
        """
        return {"message": "Label Reader API is running. Frontend not found."}
