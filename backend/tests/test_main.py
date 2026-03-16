"""
Unit tests for the main backend API.
"""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


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
