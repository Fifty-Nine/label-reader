# GEMINI.md - Label Reader Re-implementation Mandate

This document serves as the foundational mandate for the implementation of the Label Reader application. All future development must adhere to the architectural decisions and requirements outlined herein.

## Project Overview
The Label Reader is a specialized tool for digitizing handwritten or printed inventory labels using Vision-Language Models (VLMs) hosted via Ollama.

## Architectural Requirements

### 1. Backend (FastAPI)
- **Framework:** FastAPI (Python).
- **Responsibility:** Strictly a stateless REST API. It must NOT serve static files or render templates.
- **AI Orchestration:** Use the official `ollama` Python library. Manual `requests` calls to the Ollama API are prohibited.
- **Schema Validation:** Use Pydantic models for all request and response payloads.
- **Endpoints:**
  - `GET /api/models`: Returns a list of available models from the Ollama instance.
  - `POST /api/extract`: Receives an image and configuration (model name, description, date toggle) and returns structured JSON inventory data.
- **Testing:**
  - All backend logic (e.g., prompt generation, data validation) must include unit tests.
  - Tests must use a framework like `pytest`.
  - The `ollama.Client` must be mocked (`unittest.mock`) to ensure that unit tests can run without access to a live Ollama instance.
  - All new features or bug fixes must be accompanied by appropriate test coverage.

### 2. Frontend (Vue.js)
- **Framework:** Vue 3 (Composition API preferred).
- **Responsibility:** A modern, reactive Single Page Application (SPA).
- **Key Features:**
  - Dynamic model selection dropdown populated from the backend.
  - Multi-modal image input: File upload and live camera capture (using browser MediaDevices API).
  - Real-time UI state management (loading indicators, error handling, result preview).
  - Clean, responsive design (e.g., using a library like Tailwind CSS or Bootstrap).

## Functional Requirements
- **Dynamic Model Discovery:** Automatically fetch available VLMs from the Ollama service on startup/load.
- **Configurable Extraction:** Users must be able to:
  - Select the specific Ollama model to use.
  - Provide a "Label Description" to guide the VLM (e.g., "blue tape labels").
  - Toggle "Date Extraction" on/off.
- **Robust OCR Processing:** The backend must handle cleaning raw VLM output (stripping markdown backticks, etc.) and return a strictly validated JSON array.
- **Structured Display:** Extracted items and dates must be displayed in a clear, tabular format.

## Use Cases

| ID | Actor | Goal | Description |
| :--- | :--- | :--- | :--- |
| **UC-1** | User | Select Model | Select a vision-capable model from the dynamic list provided by the backend. |
| **UC-2** | User | Capture Label | Take a photo of a physical label using a mobile/web camera. |
| **UC-3** | User | Upload Image | Upload an existing `.jpg` or `.png` file containing inventory labels. |
| **UC-4** | User | Refine Prompt | Adjust the description of the labels to improve accuracy for specific media. |
| **UC-5** | System | Extract Data | Process the image via Ollama, parse the JSON response, and validate against the schema. |
| **UC-6** | User | View Results | Review the extracted item names and dates in a structured table. |

## Implementation Constraints
- **Statelessness:** The backend must not maintain session state. All configuration required for extraction must be sent with each `POST /api/extract` request.
- **Client Library:** Only the official `ollama` library should be used for interacting with the AI service.
- **No SSR:** No Jinja2 or server-side HTML rendering.
- **Image Handling:** Images should be sent to the backend as `multipart/form-data` or Base64 encoded JSON (architect's choice based on efficiency).
