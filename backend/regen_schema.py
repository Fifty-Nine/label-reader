"""Generate a schema for the backend API."""
import json
from app.main import app

schema = app.openapi()
with open('openapi.json', 'w', encoding='utf8') as f:
    json.dump(schema, f, indent=2)
