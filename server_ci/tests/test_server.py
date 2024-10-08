import openai
import os
import pytest
from guardrails import Guard, settings

# OpenAI compatible Guardrails API Guard
openai.base_url = "http://127.0.0.1:8000/guards/test-guard/openai/v1/"

openai.api_key = os.getenv("OPENAI_API_KEY") or "some key"


@pytest.mark.parametrize(
    "mock_llm_output, validation_output, validation_passed, error",
    [
        (
            "France is wonderful in the spring",
            "France is",
            True,
            False,
        ),
    ],
)
def test_guard_validation(mock_llm_output, validation_output, validation_passed, error):
    settings.use_server = True
    guard = Guard(name="test-guard")
    if error:
        with pytest.raises(Exception):
            validation_outcome = guard.validate(mock_llm_output)
    else:
        validation_outcome = guard.validate(mock_llm_output)
        assert validation_outcome.validation_passed == validation_passed
        assert validation_outcome.validated_output == validation_output


@pytest.mark.parametrize(
    "message_content, output, validation_passed, error",
    [
        (
            "Tell me about Oranges in 5 words",
            "Citrus fruit",
            True,
            False,
        ),
    ],
)
def test_server_guard_llm_integration(
    message_content, output, validation_passed, error
):
    settings.use_server = True
    guard = Guard(name="test-guard")
    messages = [{"role": "user", "content": message_content}]
    if error:
        with pytest.raises(Exception):
            validation_outcome = guard(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.0,
            )
    else:
        validation_outcome = guard(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.0,
        )
        assert (output) in validation_outcome.validated_output
        assert (validation_outcome.validation_passed) is validation_passed


@pytest.mark.parametrize(
    "message_content, output, validation_passed, error",
    [
        (
            "Write 5 words of prose.",
            "Whispers of",
            True,
            False,
        ),
    ],
)
def test_server_openai_llm_integration(
    message_content, output, validation_passed, error
):
    messages = [{"role": "user", "content": message_content}]
    if error:
        with pytest.raises(Exception):
            completion = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.0,
            )
    else:
        completion = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.0,
        )
        assert (output) in completion.choices[0].message.content
        assert (completion.guardrails["validation_passed"]) is validation_passed