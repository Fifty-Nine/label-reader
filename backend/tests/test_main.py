"""
Unit tests for the main backend API.
"""
import ollama
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app, raise_server_exceptions=False)


def test_extract_label_success(mocker):
    """
    Test successful extraction of a label image.
    """
    # Mock the ollama.Client.chat method
    mock_chat = mocker.patch("app.main.ollama_client.chat")
    mock_chat.return_value = {
        'message': {
            'content': 'Extracted label text'
        }
    }

    # Create a dummy image file
    file_content = b"fake image content"
    files = {"file": ("test.png", file_content, "image/png")}

    # Send the request
    response = client.post("/api/extract",
                           data={"model_name": "qwen3.5:9b"},
                           files=files)

    # Assertions
    assert response.status_code == 200
    assert response.json() == {"result": "Extracted label text"}
    mock_chat.assert_called_once()


def test_extract_label_success_default_model(mocker):
    """
    Test successful extraction of a label image.
    """
    # Mock the ollama.Client.chat method
    mock_chat = mocker.patch("app.main.ollama_client.chat")
    mock_chat.return_value = {
        'message': {
            'content': 'Extracted label text'
        }
    }

    # Create a dummy image file
    file_content = b"fake image content"
    files = {"file": ("test.png", file_content, "image/png")}

    # Send the request
    response = client.post("/api/extract",
                           files=files)

    # Assertions
    assert response.status_code == 200
    assert response.json() == {"result": "Extracted label text"}
    mock_chat.assert_called_once()


def test_extract_label_invalid_file_type():
    """
    Test uploading a non-image file.
    """
    # Send a non-image file
    file_content = b"fake text content"
    files = {"file": ("test.txt", file_content, "text/plain")}

    response = client.post("/api/extract",
                           data={"model_name": "qwen3.5:9b"},
                           files=files)

    assert response.status_code == 400
    assert response.json() == {"detail": "File must be an image"}


def test_extract_label_model_error_json(mocker):
    """
    Test when the model returns an error in JSON format.
    """
    mock_chat = mocker.patch("app.main.ollama_client.chat")
    mock_chat.side_effect = ollama.ResponseError(
        '{"error": "model not found"}', 404
    )

    file_content = b"fake image content"
    files = {"file": ("test.png", file_content, "image/png")}

    response = client.post("/api/extract",
                           data={"model_name": "qwen3.5:9b"},
                           files=files)

    assert response.status_code == 400
    assert 'Model not found' in response.json()['detail']


def test_extract_label_transport_error(mocker):
    """
    Test when the transport fails (e.g. failure to connect to Ollama).
    """
    mock_chat = mocker.patch("app.main.ollama_client.chat")
    mock_chat.side_effect = ollama.RequestError("Connection refused")

    file_content = b"fake image content"
    files = {"file": ("test.png", file_content, "image/png")}

    response = client.post("/api/extract",
                           data={"model_name": "qwen3.5:9b"},
                           files=files)

    assert response.status_code == 500
    assert "Connection refused" in response.json()["detail"]


def test_extract_label_non_structured_data(mocker):
    """
    Test when the model incorrectly returns non-structured data instead of
    structured data.
    """
    mock_chat = mocker.patch("app.main.ollama_client.chat")
    mock_chat.return_value = {
        'message': {
            'content': 'This is plain text, not JSON.'
        }
    }

    file_content = b"fake image content"
    files = {"file": ("test.png", file_content, "image/png")}

    response = client.post("/api/extract",
                           data={"model_name": "qwen3.5:9b"},
                           files=files)

    assert response.status_code == 200
    assert response.json() == {"result": "This is plain text, not JSON."}


def test_get_models_success(mocker):
    """
    Test successfully fetching models from the Ollama client.
    """
    mock_list = mocker.patch("app.main.ollama_client.list")
    mock_list.return_value = {
        "models": [
            {"name": "llama3:latest",
             "model": "llama3:latest",
             "modified_at": "2023-11-04T14:56:49.277302595-07:00",
             "size": 3826793677,
             "digest": "fe938a131f40e6f6d40083c9f0f430a515233eb2",
             "details": {"parent_model": "",
                         "format": "gguf",
                         "family": "llama",
                         "families": ["llama"],
                         "parameter_size": "7B",
                         "quantization_level": "Q4_0"}},
            {"name": "qwen3.5:9b",
             "model": "qwen3.5:9b",
             "modified_at": "2023-11-04T14:56:49.277302595-07:00",
             "size": 3826793677,
             "digest": "fe938a131f40e6f6d40083c9f0f430a515233eb2",
             "details": {"parent_model": "",
                         "format": "gguf",
                         "family": "llama",
                         "families": ["llama"],
                         "parameter_size": "7B",
                         "quantization_level": "Q4_0"}}
        ]
    }

    response = client.get("/api/models")

    assert response.status_code == 200
    assert response.json() == {"models": ["llama3:latest", "qwen3.5:9b"]}
    mock_list.assert_called_once()


def test_get_models_transport_error(mocker):
    """
    Test that the exception handler correctly catches
    failures when fetching models.
    """
    mock_list = mocker.patch("app.main.ollama_client.list")
    mock_list.side_effect = ollama.RequestError("Connection refused")

    response = client.get("/api/models")

    assert response.status_code == 500
    assert "Connection refused" in response.json()["detail"]
