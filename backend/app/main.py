"""
Main module for the Label Reader backend API.
"""
import os
import json
import textwrap
import traceback
from typing import Annotated, NoReturn
from fastapi import (FastAPI,
                     File,
                     Form,
                     HTTPException,
                     Request,
                     UploadFile)
from fastapi.responses import (FileResponse,
                               JSONResponse)
from ollama import Client, ResponseError as OllamaResponseError
from pydantic import BaseModel, Field, TypeAdapter

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
    visual_evidence: str = Field(
            description="Briefly describes the physical material and style "
                        "of the label. This should include details about the "
                        "label itself (e.g. blue painter's tape with "
                        "black marker, white label with black machine-printed "
                        "text, etc.)")
    text: str = Field(description="The text from the label.")


def get_model_prompt(user_desc: str = "handwritten labels on blue "
                                      "painter's tape") -> str:
    """Get the prompt for the model."""
    return textwrap.dedent(f"""
        You are an automated OCR system. Your sole function is to read
        labels from the provided image. You should extract only the text
        from each label on each labeled item.

        TARGET LABEL VISUAL DESCRIPTION:
        {user_desc}

        CRITICAL RULES:
        1. ONLY extract text that matches the TARGET LABEL VISUAL DESCRIPTION.
        2. IGNORE all commercial pre-printed text, manufacturer
           branding, or logos on the tape/sticker material itself (e.g., faint
           pre-printed branding codes.
        3. IGNORE text embossed into text, plastic, metal or other materials.

        You must return a JSON array matching this JSON Schema specification:
        <schema>
        {json.dumps(ParsedLabel.model_json_schema())}
        </schema>

        You MUST return a valid array even if there are zero or one labeled
        items.

        In some cases, you may encounter labels with multiple layers of text,
        e.g. a handwritten label on top of commercially printed text. In these
        cases you MUST only record the text maching the TARGET LABEL VISUAL
        DESCRIPTION and IGNORE any text that does not match.

        CRITICAL INSTRUCTION: Do NOT output the schema definition keys
        (such as 'properties', 'type', 'title', or 'description') in your
        final JSON. Your output must contain only the actual extracted
        data keys defined within the schema.
        """)


def model_response_error(e: Exception, response_text: str) -> NoReturn:
    """Raise an error indicating a mismatch between the model's response
    and the schema expectations."""
    raise HTTPException(
        status_code=500,
        detail='Model returned data that did not match the schema. '
               f'Model response: "{response_text!r}"'
    ) from e


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

    try:
        response = ollama_client.chat(
            model=model_name or DEFAULT_MODEL,
            format=TypeAdapter(list[ParsedLabel]).json_schema(),
            messages=[{
                'role': 'user',
                'content': get_model_prompt(),
                'images': [contents]
            }]
        )
        response_text = response['message']['content']

        return [ParsedLabel(**item)
                for item in json.loads(response_text)]
    except OllamaResponseError as e:
        if e.status_code == 404:
            raise HTTPException(
                status_code=400,
                detail='Model not found on Ollama instance.') from e
        raise e
    except json.decoder.JSONDecodeError as e:
        model_response_error(e, response_text)
    except TypeError as e:
        model_response_error(e, response_text)


class ModelList(BaseModel):
    """List of models returned from the API."""
    models: list[str] = Field(description='The list of models supported '
                                          'by the server.')
    default: str | None = Field(default=None,
                                description='The preferred default model.')


@app.get("/api/models")
def get_models() -> ModelList:
    """
    Gets the list of available models from Ollama.
    """
    models = [m['model'] for m in ollama_client.list()['models']]

    return ModelList(models=models, default=DEFAULT_MODEL)


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
