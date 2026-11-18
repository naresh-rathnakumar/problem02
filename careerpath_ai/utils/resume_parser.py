"""
Resume parsing utilities supporting PDF, DOCX, and TXT.
Integrates PyMuPDF with seamless pypdf fallback and python-docx / zipfile parser.
"""

import os
import io
import zipfile
import xml.etree.ElementTree as ET
from typing import Tuple


def parse_resume(uploaded_file) -> str:
    """Parse an uploaded file object or file path into plain text."""
    filename = getattr(uploaded_file, "name", str(uploaded_file)).lower()

    if filename.endswith(".pdf"):
        return parse_pdf(uploaded_file)
    elif filename.endswith(".docx"):
        return parse_docx(uploaded_file)
    elif filename.endswith(".txt"):
        return parse_txt(uploaded_file)
    else:
        raise ValueError(f"Unsupported resume format: {filename}. Supported formats are PDF, DOCX, TXT.")


def parse_pdf(file_source) -> str:
    """Extract text from PDF using PyMuPDF (fitz) or fallback to pypdf."""
    # Obtain bytes
    if hasattr(file_source, "read"):
        content_bytes = file_source.read()
        if hasattr(file_source, "seek"):
            file_source.seek(0)
    else:
        with open(file_source, "rb") as f:
            content_bytes = f.read()

    # Try PyMuPDF (fitz)
    try:
        import fitz
        doc = fitz.open(stream=content_bytes, filetype="pdf")
        text_parts = [page.get_text() for page in doc]
        doc.close()
        text = "\n".join(text_parts).strip()
        if text:
            return text
    except ImportError:
        pass

    # Try pypdf
    try:
        import pypdf
        reader = pypdf.PdfReader(io.BytesIO(content_bytes))
        text_parts = []
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text_parts.append(extracted)
        text = "\n".join(text_parts).strip()
        if text:
            return text
    except Exception as e:
        raise ValueError(f"PDF parsing error: {str(e)}")

    raise ValueError("Could not extract readable text from PDF. File might be empty or scanned images.")


def parse_docx(file_source) -> str:
    """Extract text from DOCX using python-docx or native XML extraction."""
    if hasattr(file_source, "read"):
        content_bytes = file_source.read()
        if hasattr(file_source, "seek"):
            file_source.seek(0)
    else:
        with open(file_source, "rb") as f:
            content_bytes = f.read()

    # Try python-docx
    try:
        from docx import Document
        doc = Document(io.BytesIO(content_bytes))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        for table in doc.tables:
            for row in table.rows:
                row_str = " | ".join(c.text.strip() for c in row.cells if c.text.strip())
                if row_str:
                    paragraphs.append(row_str)
        text = "\n".join(paragraphs).strip()
        if text:
            return text
    except ImportError:
        pass

    # Fallback to direct OOXML parsing via zipfile
    try:
        with zipfile.ZipFile(io.BytesIO(content_bytes)) as z:
            xml_content = z.read("word/document.xml")
            tree = ET.fromstring(xml_content)
            # w:t elements contain text
            ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
            texts = [node.text for node in tree.findall(".//w:t", ns) if node.text]
            return "\n".join(texts).strip()
    except Exception as e:
        raise ValueError(f"Could not parse DOCX: {str(e)}")


def parse_txt(file_source) -> str:
    """Extract text from TXT file."""
    if hasattr(file_source, "read"):
        content = file_source.read()
        if hasattr(file_source, "seek"):
            file_source.seek(0)
    else:
        with open(file_source, "rb") as f:
            content = f.read()

    if isinstance(content, bytes):
        for enc in ["utf-8", "latin-1", "cp1252"]:
            try:
                return content.decode(enc).strip()
            except UnicodeDecodeError:
                continue
        return content.decode("utf-8", errors="replace").strip()
    return str(content).strip()


def validate_file(uploaded_file, max_size_mb: int = 10) -> Tuple[bool, str]:
    """Validate file extension and size constraints."""
    filename = getattr(uploaded_file, "name", "").lower()
    ext = os.path.splitext(filename)[1]
    allowed = [".pdf", ".docx", ".txt"]

    if ext not in allowed:
        return False, f"Unsupported file type ({ext}). Allowed: {', '.join(allowed)}"

    size = getattr(uploaded_file, "size", 0)
    max_bytes = max_size_mb * 1024 * 1024
    if size > max_bytes:
        return False, f"File size exceeds {max_size_mb}MB limit ({size / (1024*1024):.1f}MB)."

    return True, "Valid file"
