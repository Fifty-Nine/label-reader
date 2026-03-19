# Label Reader Re-implementation Plan

This document outlines the step-by-step implementation plan for rebuilding the Label Reader application based on the `GEMINI.md` architectural mandate.

## Phase 0: Basic Project Structure

**DONE** 1. Create subfolders for the frontend and the backend.
**DONE** 2. **Backend:** Create basic project structure for the python backend using poetry. Include an appropriate unit testing framework and configure poetry to use a pre-commit hook with pylint, flake8, mypy and unit test checks.

## Phase 1: Core MVP - Image Upload and Basic Extraction

**DONE** 1.  **Backend:** Implement a basic `POST /api/extract` endpoint that accepts a file upload.
**DONE** 2.  **Backend:** Integrate the `ollama` client and use it in the endpoint to process the uploaded image with a **hardcoded model name** (e.g., `qwen2.5vl:7b`).
**DONE** 3.  **Backend:** Add `pytest` to the project and write an initial unit test for the `/api/extract` endpoint. The test must mock the `ollama.Client` and verify that the endpoint returns a successful response.
**DONE** 4.  **Frontend:** Initialize a new Vue 3 project (e.g., using `npm create vue@latest`).
**DONE** 5.  **Frontend:** Create a simple view with a file input and a "Submit" button.
**DONE** 6.  **Frontend:** Implement the logic to call the `POST /api/extract` endpoint upon form submission.
**DONE** 7.  **Frontend:** Display the raw JSON response returned from the backend.

## Phase 2: Dynamic Model Selection

**DONE** 1.  **Backend:** Implement the `GET /api/models` endpoint that uses the `ollama.Client` to fetch available models.
**DONE** 2.  **Backend:** Update the `/api/extract` endpoint to accept a `model_name` field in its Pydantic model. Use this value instead of the hardcoded one.
**DONE** 3.  **Backend:** Add/update unit tests for the `/api/models` endpoint and the modified `/api/extract` endpoint.
**DONE** 4.  **Frontend:** On application load, call the `/api/models` endpoint to fetch the list of available models.
**DONE** 5.  **Frontend:** Add a `<select>` dropdown to the UI and populate it with the fetched models.
**DONE** 6.  **Frontend:** Update the submit logic to include the currently selected model name in the request to `/api/extract`.

## Phase 3: Advanced Configuration & UI Polish

**DONE** 1.  **Backend:** Update the `/api/extract` Pydantic model to accept `label_desc` and `include_date` fields.
**DONE** 2.  **Backend:** Implement the `get_prompt` logic to dynamically generate the VLM prompt based on these new parameters.
**DONE** 3.  **Backend:** Write unit tests for the prompt generation logic to ensure it behaves as expected.
4.  **Frontend:** Add a text input for "Label Description" and a checkbox for "Extract Dates".
5.  **Frontend:** Pass these new configuration values in the request to `/api/extract`.
6.  **Frontend:** Instead of displaying raw JSON, parse the response and render the results in a user-friendly HTML table. Add a clear loading indicator that displays while waiting for the API.

## Phase 4: Camera Integration

1.  **Frontend:** Add UI elements to switch between File Upload and Camera modes (e.g., tabs).
2.  **Frontend:** Implement camera access using `navigator.mediaDevices.getUserMedia` and display the live video stream.
3.  **Frontend:** Add a "Capture" button. When clicked, draw the current video frame to a `<canvas>`.
4.  **Frontend:** Convert the canvas content to a `Blob` or `File` object.
5.  **Frontend:** Send this captured image to the `POST /api/extract` endpoint, reusing all existing form logic for model selection and configuration.
