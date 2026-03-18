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
    response = client.post("/api/extract", files=files)

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

    response = client.post("/api/extract", files=files)

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

    response = client.post("/api/extract", files=files)

    assert response.status_code == 500
    assert 'model not found' in response.json()["detail"]
    assert '404' in response.json()["detail"]


def test_extract_label_transport_error(mocker):
    """
    Test when the transport fails (e.g. failure to connect to Ollama).
    """
    mock_chat = mocker.patch("app.main.ollama_client.chat")
    mock_chat.side_effect = ollama.RequestError("Connection refused")

    file_content = b"fake image content"
    files = {"file": ("test.png", file_content, "image/png")}

    response = client.post("/api/extract", files=files)

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

    response = client.post("/api/extract", files=files)

    assert response.status_code == 200
    assert response.json() == {"result": "This is plain text, not JSON."}
