# Label Reader Re-implementation Plan

This document outlines the step-by-step implementation plan for rebuilding the Label Reader application based on the `GEMINI.md` architectural mandate.

## Phase 1: Core MVP - Image Upload and Basic Extraction

**DONE** 1.  Implement a basic `POST /api/extract` endpoint that accepts a file upload.
**DONE** 2.  Integrate the `ollama` client and use it in the endpoint to process the uploaded image with a **hardcoded model name** (e.g., `qwen2.5vl:7b`).
**DONE** 3.  Add `pytest` to the project and write an initial unit test for the `/api/extract` endpoint. The test must mock the `ollama.Client` and verify that the endpoint returns a successful response.

## Phase 2: Dynamic Model Selection

1.  Implement the `GET /api/models` endpoint that uses the `ollama.Client` to fetch available models.
2.  Update the `/api/extract` endpoint to accept a `model_name` field in its Pydantic model. Use this value instead of the hardcoded one.
3.  Add/update unit tests for the `/api/models` endpoint and the modified `/api/extract` endpoint.

## Phase 3: Advanced Configuration & UI Polish

1.  Update the `/api/extract` Pydantic model to accept `label_desc` and `include_date` fields.
2.  Implement the `get_prompt` logic to dynamically generate the VLM prompt based on these new parameters.
3.  Write unit tests for the prompt generation logic to ensure it behaves as expected.

