"""Test secret redaction."""
import pytest
from app.redaction import redact_string, redact_dict

# GitHub tokens are 36 chars after 'ghp_'
GITHUB_TOKEN = "ghp_" + "a" * 36
GITHUB_PAT = "github_pat_" + "a" * 40
BEARER_TOKEN = "ya29." + "a" * 30
SK_TOKEN = "sk-" + "a" * 25  # must be >= 20 chars for pattern
PASSWORD_SECRET = "password=supersecret123"
AUTH_HEADER = "Authorization: Bearer xoxb-1234567890-abcdefghijk"


class TestRedactKnownPatterns:
    def test_github_token(self):
        assert "[REDACTED]" in redact_string(GITHUB_TOKEN)

    def test_github_pat(self):
        assert "[REDACTED]" in redact_string(GITHUB_PAT)

    def test_bearer_token(self):
        result = redact_string(f"Bearer {BEARER_TOKEN}")
        assert "Bearer [REDACTED]" in result

    def test_sk_token(self):
        assert "[REDACTED]" in redact_string(SK_TOKEN)

    def test_password_field(self):
        result = redact_string(PASSWORD_SECRET)
        assert "[KEY_REDACTED]" in result or "[REDACTED]" in result

    def test_auth_header(self):
        result = redact_string(AUTH_HEADER)
        assert "[REDACTED]" in result


class TestRedactDict:
    def test_nested_dict(self):
        data = {"nested": {"token": GITHUB_TOKEN}, "safe": "hello"}
        result = redact_dict(data)
        assert "[REDACTED]" in str(result)
        assert "hello" == result["safe"]

    def test_list_of_strings(self):
        data = ["normal", SK_TOKEN]
        result = redact_dict(data)
        assert "[REDACTED]" in str(result)
        assert "normal" == result[0]

    def test_clean_text_preserved(self):
        assert redact_string("hello world") == "hello world"
