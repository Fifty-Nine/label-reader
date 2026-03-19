"""
Main module for the Label Reader backend API.
"""
import os
import json
import traceback
from typing import Annotated
from fastapi import (FastAPI,
                     File,
                     Form,
                     HTTPException,
                     Request,
                     UploadFile)
from fastapi.responses import (FileResponse,
                               JSONResponse)
from ollama import Client, ResponseError as OllamaResponseError
from pydantic import BaseModel, Field

app = FastAPI(title="Label Reader API")

# Use environment variable for Ollama host,
# fallback to the dev instance from GEMINI.md
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "https://ollama.home.trprince.com")
DEFAULT_MODEL = os.getenv("OLLAMA_DEFAULT_MODEL", "qwen3.5:9b")
ollama_client = Client(host=OLLAMA_HOST)

# Configuration for static files (frontend)
STATIC_DIR = os.getenv("STATIC_DIR", "static")


@app.exception_handler(Exception)
def custom_exception_handler(_request: Request, ex: Exception):
    """Handle arbitrary exceptions thrown by handlers."""
    # Print the exception backtrace to the server log
    traceback.print_exception(type(ex), ex, ex.__traceback__)

    tb = '\n'.join(traceback.format_exception(type(ex),
                                              ex,
                                              ex.__traceback__))
    return JSONResponse(
        status_code=500,
        content={'detail': f"Internal Server Error: {tb}"}
    )


class ParsedLabel(BaseModel):
    """Represents a label parsed from an image."""
    text: str = Field(description="The (non-date) text parsed from an "
                                  "item label.")


@app.post("/api/extract")
async def extract_label(
    model_name: Annotated[str | None, Form()] = None,
    file: UploadFile = File(...)
) -> list[ParsedLabel]:
    """
    Extracts structured data from an uploaded image of a label.
    """
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    contents = await file.read()
    prompt = (
        "You are an automated OCR system. Your sole function is to read "
        "labels from the provided image. You should extract only the text "
        "from each label on each labeled item. Do not extract any background "
        "text. You must return a JSON array matching this schema: "
        f"{json.dumps(ParsedLabel.model_json_schema())} "
        "You must return a valid array even if there are zero or "
        "one labeled items."
    )

    try:
        response = ollama_client.chat(
            model=model_name or DEFAULT_MODEL,
            format='json',
            messages=[{
                'role': 'user',
                'content': prompt,
                'images': [contents]
            }]
        )

        return [ParsedLabel(**item)
                for item in json.loads(response['message']['content'])]
    except OllamaResponseError as e:
        if e.status_code == 404:
            raise HTTPException(
                status_code=400,
                detail='Model not found on Ollama instance.') from e
        raise e
    except json.decoder.JSONDecodeError as e:
        raise HTTPException(
                status_code=500,
                detail='Model returned data that did '
                       'not match the schema.') from e


class ModelList(BaseModel):
    """List of models returned from the API."""
    models: list[str] = Field(description='The list of models supported '
                                          'by the server.')


@app.get("/api/models")
def get_models() -> ModelList:
    """
    Gets the list of available models from Ollama.
    """
    models = [m['model'] for m in ollama_client.list()['models']]

    return ModelList(models=models)


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
