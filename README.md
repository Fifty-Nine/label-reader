# Label Reader

This project is a specialized web application designed to digitize handwritten
or printed inventory labels using Vision-Language Models (VLMs). It processes
images of physical labels and turns them into structured data for the purposes
of keeping digital records up-to-date with real-world inventories.

## Project Architecture

This repository is divided into two main components:

- **`backend/`**: A stateless REST API built with Python and **FastAPI**. It
  handles image processing, orchestrates interactions with the **Ollama** AI
  service using the official Python client, and ensures strict schema
  validation using **Pydantic**.
- **`frontend/`**: A modern Single Page Application (SPA) built with **Vue 3**
  (Composition API) and **Vite**. It provides a reactive UI for multi-modal
	image input (camera capture and file upload), model selection, and real-time
	structured data display.

## Key Features

- **Dynamic Model Discovery:** Automatically fetches available VLMs from a
  configured Ollama instance on startup.
- **Multi-modal Input:** Capture photos using mobile/web cameras or upload
  existing `.jpg` or `.png` images.
- **Configurable Extraction:** Customize the VLM extraction by selecting the
  model, providing "Label Descriptions" to guide accuracy, and toggling specific
	extractions like dates.
- **Robust OCR Processing:** Backend logic cleans raw VLM output and returns
  strictly validated JSON.
- **Structured Display:** View extracted item names and dates in a clean,
  tabular format.

## Technologies

### Backend
- **Python >= 3.11**
- **FastAPI** & Uvicorn
- **Ollama Python Library**
- **Pydantic**
- **Poetry** (Dependency Management)
- **Pytest** (Testing)

### Frontend
- **Node.js**
- **Vue 3** & Vue Router
- **TypeScript**
- **Vite**
- **Oxlint, ESLint, Prettier**

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js (v20.19.0+ or v22.12.0+)
- An accessible [Ollama](https://ollama.com/) instance with vision-capable
  models (e.g., `llava`).

### Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Install dependencies using Poetry:
   ```bash
   poetry install
   ```
3. Run the FastAPI development server:
   ```bash
   poetry run uvicorn app.main:app --reload
   ```

### Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the Vite development server:
   ```bash
   npm run dev
   ```

## Development & Design Guidelines

For detailed requirements, constraints, and use cases, please review the project documentation:
- **`DESIGN.md`**: Core architectural requirements, functional use-cases, and implementation constraints.
- **`GEMINI.md`**: Specific mandates for AI-assisted development, including sandboxed environment cache configurations for tools like `poetry` and `pre-commit`.
- **`IDEAS.md`**: Future project goals and potential enhancements.
