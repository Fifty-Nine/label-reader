"""
Unit tests for the prompt generation logic.
"""
import json
from app.main import (get_model_prompt,
                      parsed_label_schema,
                      dated_label_schema)


def test_get_model_prompt_default():
    """
    Test prompt generation with default parameters.
    It should not include 'date' in the schema definition.
    """
    prompt = get_model_prompt(schema=parsed_label_schema)
    assert "handwritten labels on blue painter's tape" in prompt

    # Extract the schema block from the prompt for validation
    schema_str = prompt.split("<schema>")[1].split("</schema>")[0].strip()
    schema_json = json.loads(schema_str)

    # Check that 'date' is not present in properties
    assert 'date' not in schema_json.get('properties', {})


def test_get_model_prompt_custom_desc():
    """
    Test prompt generation with a custom label description.
    """
    custom_desc = "printed QR codes on white stickers"
    prompt = get_model_prompt(schema={}, user_desc=custom_desc)

    assert custom_desc in prompt
    assert ("TARGET LABEL VISUAL DESCRIPTION:\n"
            f"{custom_desc}") in prompt


def test_get_model_prompt_include_date():
    """
    Test prompt generation when include_date is True.
    It should include 'date' in the schema definition.
    """
    prompt = get_model_prompt(schema=dated_label_schema, include_date=True)

    schema_str = prompt.split("<schema>")[1].split("</schema>")[0].strip()
    schema_json = json.loads(schema_str)

    assert schema_json == dated_label_schema
    assert "Today's date is" in prompt
