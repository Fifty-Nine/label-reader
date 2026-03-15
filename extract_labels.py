import base64
import requests
import json
import sys
import os

# Configuration
OLLAMA_URL = "https://ollama.home.trprince.com/api/generate"
MODEL_NAME = "qwen2.5vl:7b"

def encode_image_to_base64(image_path):
    """Reads an image file and converts it to a base64 string."""
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found at path: {image_path}")
    
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def process_freezer_inventory(image_path):
    """Sends the image and prompt to the local Ollama instance."""
    base64_image = encode_image_to_base64(image_path)
    
    prompt = (
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

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "images": [base64_image],
        "stream": False,
        "options": {
            "temperature": 0.0 # Force deterministic output
        }
    }

    response = requests.post(OLLAMA_URL, json=payload)
    response.raise_for_status()
    
    raw_output = response.json().get("response", "").strip()
    
    # Fallback cleanup in case the model ignores markdown constraints
    if raw_output.startswith("```"):
        raw_output = raw_output.strip("`").replace("json\n", "", 1).strip()
        
    try:
        structured_data = json.loads(raw_output)
        return structured_data
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON from model output.\nRaw Output: {raw_output}") from e

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extract_labels.py <path_to_image>")
        sys.exit(1)
        
    target_image = sys.argv[1]
    
    try:
        inventory_result = process_freezer_inventory(target_image)
        print(json.dumps(inventory_result, indent=2))
    except Exception as error:
        print(f"Error during execution: {error}")
