import pytest
from fastapi import HTTPException

from app.api.public_submissions import validate_submission_fields


WIDGET_FIELDS = [
    {
        "name": "name",
        "type": "text",
        "required": True,
    },
    {
        "name": "email",
        "type": "email",
        "required": True,
    },
]


def test_valid_submission():
    data = {
        "name": "Test User",
        "email": "test@example.com",
    }

    validate_submission_fields(
        widget_fields=WIDGET_FIELDS,
        submitted_data=data,
    )


def test_missing_required_field():
    data = {
        "name": "Test User",
    }

    with pytest.raises(HTTPException) as exc:
        validate_submission_fields(
            widget_fields=WIDGET_FIELDS,
            submitted_data=data,
        )

    assert exc.value.status_code == 422
    assert exc.value.detail == "Missing required field: email"


def test_unexpected_field():
    data = {
        "name": "Test User",
        "email": "test@example.com",
        "phone": "1234567890",
    }

    with pytest.raises(HTTPException) as exc:
        validate_submission_fields(
            widget_fields=WIDGET_FIELDS,
            submitted_data=data,
        )

    assert exc.value.status_code == 422
    assert exc.value.detail == "Unexpected submission field"


def test_invalid_email():
    data = {
        "name": "Test User",
        "email": "not-an-email",
    }

    with pytest.raises(HTTPException) as exc:
        validate_submission_fields(
            widget_fields=WIDGET_FIELDS,
            submitted_data=data,
        )

    assert exc.value.status_code == 422
    assert exc.value.detail == "Invalid email field: email"


def test_invalid_text_field():
    data = {
        "name": 123,
        "email": "test@example.com",
    }

    with pytest.raises(HTTPException) as exc:
        validate_submission_fields(
            widget_fields=WIDGET_FIELDS,
            submitted_data=data,
        )

    assert exc.value.status_code == 422
    assert exc.value.detail == "Invalid text field: name"