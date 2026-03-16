import base64
import requests
import json
import os
import logging
import re
from datetime import datetime
from fastapi import FastAPI, Request, File, UploadFile, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Configuration
OLLAMA_URL = os.getenv("OLLAMA_URL")
MODEL_NAME = os.getenv("MODEL_NAME", "qwen2.5vl:7b")

def get_prompt(label_desc: str = "handwritten labels on pieces of tape", include_date: bool = True):
    current_date = datetime.now().strftime("%Y-%m-%d")

    date_instruction = "and the date " if include_date else ""
    date_format = "Each object has an 'item' key and a 'date' key." if include_date else "Each object has an 'item' key."
    date_example = ', "date": "2026-03-23"' if include_date else ""
    date_constraints = (
        "- Assume US-style (MM/DD/YY or MM/DD/YYYY) input dates.\n"
        "- For 2-digit years (e.g., '26'), assume the current century (e.g., '2026').\n"
        "- Output dates must be ISO 8601 (YYYY-MM-DD).\n"
    ) if include_date else ""

    return (
        f"You are an automated optical character recognition system. Your sole function is to read {label_desc} in the provided image. "
        f"Today's date is {current_date}. "
        f"Extract the name of the item {date_instruction}written on each label. "
        "\n\n"
        "RESPONSE FORMAT:\n"
        f"1. If labels matching the description are found: Return a valid JSON array of objects. {date_format}\n"
        "2. If no labels are found or if the labels do not match the description above: Return a JSON object with an 'error' key explaining why.\n"
        "\n\n"
        "CONSTRAINTS:\n"
        "- Output ONLY the raw JSON.\n"
        "- No markdown formatting (no ```json).\n"
        "- No conversational text.\n"
        f"{date_constraints}"
        "\n\n"
        "EXAMPLES:\n"
        f"Success: [{{ \"item\": \"Pork loin\"{date_example} }}]\n"
        "Failure: {{ \"error\": \"No labels detected.\" }}"
    )

@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/process", response_class=HTMLResponse)
async def process_image(
    request: Request,
    file: UploadFile = File(...),
    label_desc: Optional[str] = Form(None),
    include_date: Optional[str] = Form(None),
    label_desc_hidden: Optional[str] = Form(None),
    include_date_hidden: Optional[str] = Form(None)
):
    if not OLLAMA_URL:
        logger.error("OLLAMA_URL is not configured.")
        return templates.TemplateResponse("index.html", {
            "request": request,
            "error": "OLLAMA_URL is not configured. Please set it as an environment variable."
        })

    # Resolve parameters from either standard or hidden fields
    final_label_desc = label_desc or label_desc_hidden or "handwritten labels on pieces of tape"

    # Handle boolean conversion from string "true"/"false"
    include_date_val = include_date or include_date_hidden
    final_include_date = True if include_date_val in [True, "true", "True", "on"] else False

    logger.info(f"Received file: {file.filename}, size: {file.size if hasattr(file, 'size') else 'unknown'}")
    logger.info(f"Label description: {final_label_desc}, Include date: {final_include_date}")

    try:
        # Read file and encode to base64
        contents = await file.read()
        logger.info(f"Read {len(contents)} bytes from uploaded file.")

        if len(contents) == 0:
            return templates.TemplateResponse("index.html", {
                "request": request,
                "error": "The uploaded file is empty."
            })

        base64_image = base64.b64encode(contents).decode('utf-8')

        current_prompt = get_prompt(final_label_desc, final_include_date)

        # Prepare payload for Ollama
        payload = {
            "model": MODEL_NAME,
            "prompt": current_prompt,
            "images": [base64_image],
            "stream": False,
            "options": {
                "temperature": 0.0 # Force deterministic output
            }
        }

        # Log the request (excluding the image content)
        logger.info(f"Sending request to Ollama. Model: {MODEL_NAME}")
        logger.info(f"Using Prompt: {current_prompt}")

        # Call Ollama API
        response = requests.post(OLLAMA_URL, json=payload, timeout=60)
        response.raise_for_status()

        raw_output = response.json().get("response", "").strip()

        # Log the raw response
        logger.info(f"Raw response from Ollama: {raw_output}")

        # Fallback cleanup in case the model ignores markdown constraints
        if "```" in raw_output:
            match = re.search(r'```(?:json)?\s*(.*?)\s*```', raw_output, re.DOTALL)
            if match:
                raw_output = match.group(1).strip()
            else:
                raw_output = raw_output.strip("`").replace("json\n", "", 1).strip()

        try:
            structured_data = json.loads(raw_output)

            # 1. Handle explicit error object from model
            if isinstance(structured_data, dict) and "error" in structured_data:
                return templates.TemplateResponse("index.html", {
                    "request": request,
                    "error": structured_data["error"]
                })

            # 2. Handle empty list or empty response as a "not found" error
            if not structured_data or (isinstance(structured_data, list) and len(structured_data) == 0):
                return templates.TemplateResponse("index.html", {
                    "request": request,
                    "error": "No labels were detected in this image."
                })

            # Ensure structured_data is a list for the success table
            if not isinstance(structured_data, list):
                structured_data = [structured_data]

            return templates.TemplateResponse("index.html", {
                "request": request,
                "results": structured_data
            })
        except json.JSONDecodeError as e:
            logger.error(f"JSON Decode Error: {e}. Raw Output: {raw_output}")
            error_msg = f"Failed to parse JSON from model output. The model might be having trouble with this image."
            return templates.TemplateResponse("index.html", {"request": request, "error": error_msg})

    except Exception as e:
        logger.exception("An error occurred during image processing")
        return templates.TemplateResponse("index.html", {"request": request, "error": str(e)})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
