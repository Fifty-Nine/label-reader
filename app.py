import base64
import requests
import json
import os
from fastapi import FastAPI, Request, File, UploadFile
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Configuration
OLLAMA_URL = "https://ollama.home.trprince.com/api/generate"
MODEL_NAME = "qwen2.5vl:7b"

PROMPT = (
    "You are an automated optical character recognition system. Your sole function is to read "
    "handwritten labels on pieces of tape in the provided image. "
    "Extract the name of the food item and the date written on each piece of tape. "
    "Output strictly a valid JSON array of objects, where each object has an 'item' key and a 'date' key. "
    "Do not wrap the JSON in markdown blocks (e.g., ```json). "
    "Do not include any explanations, greetings, or conversational text. "
    "Output dates should be formatted according to ISO 8601 (YYYY-MM-DD). You can assume that any "
    "dates on labels follow a US-style month-day-year format. "
    "Example Output: "
    '[{"item": "Pork loin", "date": "2023-03-23"}, {"item": "French onion soup", "date": "2024-09-18"}]'
)

@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/process", response_class=HTMLResponse)
async def process_image(request: Request, file: UploadFile = File(...)):
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

        # Call Ollama API
        response = requests.post(OLLAMA_URL, json=payload, timeout=60)
        response.raise_for_status()
        
        raw_output = response.json().get("response", "").strip()
        
        # Fallback cleanup in case the model ignores markdown constraints
        if raw_output.startswith("```"):
            raw_output = raw_output.strip("`").replace("json\n", "", 1).strip()
            
        try:
            structured_data = json.loads(raw_output)
            # Ensure structured_data is a list
            if not isinstance(structured_data, list):
                structured_data = [structured_data]
            
            return templates.TemplateResponse("index.html", {
                "request": request,
                "results": structured_data
            })
        except json.JSONDecodeError as e:
            error_msg = f"Failed to parse JSON from model output: {raw_output}"
            return templates.TemplateResponse("index.html", {"request": request, "error": error_msg})

    except Exception as e:
        return templates.TemplateResponse("index.html", {"request": request, "error": str(e)})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
