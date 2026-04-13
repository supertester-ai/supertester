from unittest.mock import patch, MagicMock
from pathlib import Path
import tempfile
import json
import pytest
from claude_runner import claude_call, extract_json


def test_extract_json_plain():
    """Test extracting plain JSON from text."""
    assert extract_json('{"a": 1}') == {"a": 1}


def test_extract_json_in_code_fence():
    """Test extracting JSON from ```json code fence."""
    text = 'some text\n```json\n{"a": 1}\n```\ntrailing'
    assert extract_json(text) == {"a": 1}


def test_extract_json_missing_returns_none():
    """Test that extract_json returns None when no JSON found."""
    assert extract_json('no json here') is None


@patch('claude_runner.subprocess.run')
def test_claude_call_writes_output(mock_run, tmp_path):
    """Test that claude_call writes output to file."""
    mock_run.return_value = MagicMock(stdout='hello world', returncode=0)
    out = tmp_path / "out.txt"
    result = claude_call("prompt", str(out))
    assert result == "hello world"
    assert out.read_text(encoding='utf-8') == "hello world"


@patch('claude_runner.subprocess.run')
def test_claude_call_parses_json(mock_run, tmp_path):
    """Test that claude_call can parse JSON response."""
    mock_run.return_value = MagicMock(stdout='```json\n{"x": 42}\n```', returncode=0)
    out = tmp_path / "out.json"
    result = claude_call("p", str(out), parse_json=True)
    assert result == {"x": 42}
