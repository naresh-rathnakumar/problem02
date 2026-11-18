"""
Unit tests for resume parsing utilities (PDF, DOCX, TXT).
"""

import os
import io
import pytest
from utils.resume_parser import parse_txt, validate_file


def test_parse_txt():
    content = "John Doe\nSoftware Engineer\nPython, Docker, SQL"
    buffer = io.BytesIO(content.encode("utf-8"))
    buffer.name = "resume.txt"
    extracted = parse_txt(buffer)
    assert "John Doe" in extracted
    assert "Python" in extracted


def test_validate_file():
    class DummyFile:
        def __init__(self, name, size):
            self.name = name
            self.size = size

    valid_f = DummyFile("resume.pdf", 1024 * 1024)
    ok, msg = validate_file(valid_f)
    assert ok is True

    bad_ext = DummyFile("resume.exe", 1024)
    ok, msg = validate_file(bad_ext)
    assert ok is False
    assert "Unsupported" in msg

    too_large = DummyFile("resume.pdf", 25 * 1024 * 1024)
    ok, msg = validate_file(too_large, max_size_mb=10)
    assert ok is False
    assert "exceeds" in msg
