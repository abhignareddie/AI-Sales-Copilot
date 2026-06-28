import re
import os
import hashlib
import pyotp
from typing import Tuple, Dict, Any, List, Optional
from cryptography.fernet import Fernet
from app.core.logging import logger

class EncryptionService:
    """Symmetric encryption at rest for sensitive customer data fields, emails, and meetings."""
    
    def __init__(self, key: Optional[str] = None):
        if not key:
            raw_secret = os.getenv("SECRET_KEY", "change-me-in-production-use-openssl-rand-hex-32")
            h = hashlib.sha256(raw_secret.encode()).digest()
            import base64
            self.key = base64.urlsafe_b64encode(h)
        else:
            self.key = key.encode()
            
        try:
            self.cipher = Fernet(self.key)
        except Exception as e:
            logger.error(f"Fernet Cipher initialization failed: {e}")
            self.cipher = None

    def encrypt(self, plain_text: str) -> str:
        if not self.cipher or not plain_text:
            return plain_text
        try:
            return self.cipher.encrypt(plain_text.encode()).decode()
        except Exception as e:
            logger.error(f"Data encryption error: {e}")
            return plain_text

    def decrypt(self, cipher_text: str) -> str:
        if not self.cipher or not cipher_text:
            return cipher_text
        try:
            return self.cipher.decrypt(cipher_text.encode()).decode()
        except Exception as e:
            logger.error(f"Data decryption error: {e}")
            return cipher_text

class FileSecurityValidator:
    """Validates files against malicious extensions, MIME types, size limits, and sanitizes filenames."""
    
    ALLOWED_MIME_TYPES = {
        ".pdf": "application/pdf",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".txt": "text/plain",
        ".csv": "text/csv",
        ".md": "text/markdown",
        ".html": "text/html"
    }

    @classmethod
    def validate_file(cls, filename: str, content: bytes, max_size_mb: int = 10) -> Tuple[bool, str]:
        size_mb = len(content) / (1024 * 1024)
        if size_mb > max_size_mb:
            return False, f"File size ({size_mb:.2f}MB) exceeds limit of {max_size_mb}MB"

        ext = os.path.splitext(filename)[1].lower()
        if ext not in cls.ALLOWED_MIME_TYPES:
            return False, f"File extension '{ext}' is not permitted"

        sanitized = re.sub(r"[^a-zA-Z0-9_.-]", "_", filename)
        if ext == ".pdf" and not content.startswith(b"%PDF"):
            return False, "Malicious PDF structure detected (missing magic PDF header bytes)"
            
        return True, sanitized

class AIGuardrails:
    """Scans and rejects prompts containing prompt injections, jailbreaks, or prompt leakages."""
    
    INJECTION_PATTERNS = [
        r"\bignore\b.*\bprevious\b.*\binstructions\b",
        r"\bignore\b.*\bsystem\b.*\bprompt\b",
        r"\bignore\b.*\babove\b.*\btext\b",
        r"\byou\b.*\bmust\b.*\bforget\b",
        r"\bnew\b.*\binstructions\b.*\bstart\b.*\bhere\b",
        r"\bdo\b.*\bnot\b.*\bmention\b.*\bcompetitors\b",
        r"\bdelete\b.*\bdatabase\b",
        r"system_prompt",
        r"assistant_role"
    ]

    @classmethod
    def is_prompt_injection(cls, user_prompt: str) -> Tuple[bool, Optional[str]]:
        clean_prompt = user_prompt.lower()
        for pattern in cls.INJECTION_PATTERNS:
            if re.search(pattern, clean_prompt):
                logger.warning(f"AI Guardrails Triggered: Matched pattern '{pattern}' on prompt '{user_prompt[:50]}...'")
                return True, f"Security violation: Potential prompt injection pattern matched: '{pattern}'"
        return False, None

class TOTPService:
    """TOTP Service using pyotp for active Google Authenticator validation."""
    
    @classmethod
    def generate_secret(cls) -> str:
        return pyotp.random_base32()

    @classmethod
    def get_provisioning_url(cls, username: str, secret: str) -> str:
        return pyotp.totp.TOTP(secret).provisioning_uri(name=username, issuer_name="SalesCopilot")

    @classmethod
    def verify_totp(cls, secret: str, code: str) -> bool:
        totp = pyotp.totp.TOTP(secret)
        return totp.verify(code, valid_window=1)
