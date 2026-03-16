import base64
import requests
import json
import os
import logging
import re
from fastapi import FastAPI, Request, File, UploadFile
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Configuration
OLLAMA_URL = os.getenv("OLLAMA_URL")
MODEL_NAME = os.getenv("MODEL_NAME", "qwen2.5vl:7b")

PROMPT = (
    "You are an automated optical character recognition system. Your sole function is to read "
    "handwritten labels on pieces of tape in the provided image. "
    "Extract the name of the food item and the date written on each piece of tape. "
    "\n\n"
    "RESPONSE FORMAT:\n"
    "1. If labels on tape are found: Return a valid JSON array of objects, each with 'item' and 'date' keys.\n"
    "2. If there are no labels, or the only labels found are not on tape: Return a JSON object with an 'error' key explaining that no labels were detected.\n"
    "\n\n"
    "CONSTRAINTS:\n"
    "- Output ONLY the raw JSON.\n"
    "- No markdown formatting (no ```json).\n"
    "- No conversational text.\n"
    "- Dates must be ISO 8601 (YYYY-MM-DD).\n"
    "- Assume US-style (MM-DD-YYYY) input dates.\n"
    "\n\n"
    "EXAMPLES:\n"
    "Success: [{\"item\": \"Pork loin\", \"date\": \"2023-03-23\"}]\n"
    "Failure: {\"error\": \"No handwritten labels detected on tape in this image.\"}"
)

@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/process", response_class=HTMLResponse)
async def process_image(request: Request, file: UploadFile = File(...)):
    if not OLLAMA_URL:
        logger.error("OLLAMA_URL is not configured.")
        return templates.TemplateResponse("index.html", {
            "request": request,
            "error": "OLLAMA_URL is not configured. Please set it as an environment variable."
        })
    try:
        # Read file and encode to base64
        contents = await file.read()
        base64_image = base64.b64encode(contents).decode('utf-8')

        # Prepare payload for Ollama
        payload = {
            "model": MODEL_NAME,
            "prompt": PROMPT,
            "images": [base64_image],
            "stream": False,
            "options": {
                "temperature": 0.0 # Force deterministic output
            }
        }

        # Log the request (excluding the image content)
        logger.info(f"Sending request to Ollama. Model: {MODEL_NAME}")

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
