import os
import hashlib
import re
from typing import Dict, Any, List, Optional
from pathlib import Path
import csv
import io

from pypdf import PdfReader
from docx import Document as DocxDocument
from app.core.logging import logger
from app.core.exceptions import HTTPException

class DocumentProcessor:
    """Ingests and parses multiple document formats and extracts content and metadata."""
    
    SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt", ".csv", ".md", ".html"}
    
    @staticmethod
    def compute_hash(content: bytes) -> str:
        """Compute SHA-256 hash of the content to check for duplicates."""
        return hashlib.sha256(content).hexdigest()

    @classmethod
    def validate_file(cls, file_path: str, max_size_mb: int = 10) -> None:
        """Validate file exists, size is within limit, and extension is supported."""
        path = Path(file_path)
        if not path.exists():
            raise ValueError(f"File not found: {file_path}")
            
        ext = path.suffix.lower()
        if ext not in cls.SUPPORTED_EXTENSIONS:
            raise ValueError(f"Unsupported file extension: {ext}. Supported: {cls.SUPPORTED_EXTENSIONS}")
            
        size_mb = path.stat().st_size / (1024 * 1024)
        if size_mb > max_size_mb:
            raise ValueError(f"File size ({size_mb:.2f} MB) exceeds maximum limit of {max_size_mb} MB")

    @classmethod
    def parse(cls, file_path: str) -> Dict[str, Any]:
        """Parses a document based on its extension and returns text content and metadata."""
        cls.validate_file(file_path)
        path = Path(file_path)
        ext = path.suffix.lower()
        
        with open(file_path, "rb") as f:
            file_bytes = f.read()
            
        file_hash = cls.compute_hash(file_bytes)
        
        try:
            if ext == ".pdf":
                result = cls._parse_pdf(file_bytes)
            elif ext == ".docx":
                result = cls._parse_docx(file_bytes)
            elif ext == ".csv":
                result = cls._parse_csv(file_bytes)
            elif ext in {".txt", ".md", ".html"}:
                result = cls._parse_text_like(file_bytes, ext)
            else:
                raise ValueError(f"Unhandled file extension: {ext}")
        except Exception as e:
            logger.error(f"Error parsing file {file_path}: {e}", exc_info=True)
            raise ValueError(f"Failed to parse document: {str(e)}")
            
        # Add common metadata
        result["metadata"].update({
            "file_name": path.name,
            "file_path": file_path,
            "file_size": len(file_bytes),
            "file_hash": file_hash,
            "extension": ext,
        })
        
        return result

    @classmethod
    def _parse_pdf(cls, file_bytes: bytes) -> Dict[str, Any]:
        reader = PdfReader(io.BytesIO(file_bytes))
        text_parts = []
        headings = []
        
        for i, page in enumerate(reader.pages):
            page_text = page.extract_text() or ""
            text_parts.append(page_text)
            
            # Simple heading heuristic: lines that are short, uppercase or start with numbers on page start
            for line in page_text.split("\n"):
                clean_line = line.strip()
                if 3 < len(clean_line) < 100 and (
                    clean_line.isupper() or 
                    re.match(r"^\d+(\.\d+)*\s+[A-Z]", clean_line) or 
                    clean_line.startswith(("Section", "Chapter", "Introduction", "Conclusion", "Summary"))
                ):
                    headings.append({"text": clean_line, "page": i + 1})

        # Extract doc info metadata
        info = reader.metadata or {}
        metadata = {
            "title": info.get("/Title", ""),
            "author": info.get("/Author", ""),
            "subject": info.get("/Subject", ""),
            "creator": info.get("/Creator", ""),
            "producer": info.get("/Producer", ""),
            "pages": len(reader.pages),
            "headings": headings[:50],  # cap at 50 headings
        }
        
        return {
            "content": "\n".join(text_parts),
            "metadata": metadata
        }

    @classmethod
    def _parse_docx(cls, file_bytes: bytes) -> Dict[str, Any]:
        doc = DocxDocument(io.BytesIO(file_bytes))
        text_parts = []
        headings = []
        
        for para in doc.paragraphs:
            text = para.text.strip()
            if not text:
                continue
            text_parts.append(text)
            # Check for heading styles
            if para.style and para.style.name.startswith("Heading"):
                headings.append({"text": text, "style": para.style.name})
                
        # Basic properties
        core_properties = doc.core_properties
        metadata = {
            "title": core_properties.title or "",
            "author": core_properties.author or "",
            "subject": core_properties.subject or "",
            "keywords": core_properties.keywords or "",
            "headings": headings[:50],
        }
        
        return {
            "content": "\n".join(text_parts),
            "metadata": metadata
        }

    @classmethod
    def _parse_csv(cls, file_bytes: bytes) -> Dict[str, Any]:
        text_stream = io.StringIO(file_bytes.decode("utf-8", errors="ignore"))
        reader = csv.reader(text_stream)
        rows = list(reader)
        
        text_parts = []
        for i, row in enumerate(rows):
            text_parts.append(", ".join(row))
            
        metadata = {
            "rows_count": len(rows),
            "columns_count": len(rows[0]) if rows else 0,
            "title": "CSV Export",
        }
        
        return {
            "content": "\n".join(text_parts),
            "metadata": metadata
        }

    @classmethod
    def _parse_text_like(cls, file_bytes: bytes, ext: str) -> Dict[str, Any]:
        text = file_bytes.decode("utf-8", errors="ignore")
        headings = []
        
        if ext == ".md":
            # Extract markdown headings like # Heading
            for line in text.split("\n"):
                match = re.match(r"^(#{1,6})\s+(.+)$", line.strip())
                if match:
                    headings.append({"level": len(match.group(1)), "text": match.group(2).strip()})
        elif ext == ".html":
            # Strip simple HTML tags and extract headers
            for header in re.findall(r"<h([1-6])>(.*?)</h\1>", text, re.IGNORECASE | re.DOTALL):
                clean_h = re.sub(r"<[^>]*>", "", header[1]).strip()
                headings.append({"level": int(header[0]), "text": clean_h})
            text = re.sub(r"<script.*?>.*?</script>", "", text, flags=re.DOTALL | re.IGNORECASE)
            text = re.sub(r"<style.*?>.*?</style>", "", text, flags=re.DOTALL | re.IGNORECASE)
            text = re.sub(r"<[^>]*>", " ", text)
            text = re.sub(r"\s+", " ", text).strip()
            
        metadata = {
            "headings": headings[:50],
            "title": headings[0]["text"] if headings else Path(ext).stem
        }
        
        return {
            "content": text,
            "metadata": metadata
        }
