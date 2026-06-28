import uuid
import aiofiles
from pathlib import Path
from fastapi import UploadFile, HTTPException, status
from app.core.config import settings
from app.core.logging import logger


async def save_upload_file(file: UploadFile, subfolder: str = "") -> dict:
    """Save an uploaded file and return metadata."""
    ext = Path(file.filename).suffix.lower() if file.filename else ""
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type '{ext}' not allowed. Allowed: {settings.ALLOWED_EXTENSIONS}",
        )
    content = await file.read()
    if len(content) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds maximum of {settings.MAX_UPLOAD_SIZE // (1024 * 1024)}MB",
        )
    unique_name = f"{uuid.uuid4().hex}{ext}"
    upload_dir = Path(settings.UPLOAD_DIR) / subfolder
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = upload_dir / unique_name
    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)
    logger.info(f"File uploaded: {file.filename} -> {file_path}")
    return {
        "original_name": file.filename, "stored_name": unique_name,
        "file_path": str(file_path), "file_size": len(content),
        "content_type": file.content_type, "extension": ext,
    }


def delete_upload_file(file_path: str) -> bool:
    """Delete an uploaded file."""
    try:
        path = Path(file_path)
        if path.exists():
            path.unlink()
            logger.info(f"File deleted: {file_path}")
            return True
        return False
    except Exception as e:
        logger.error(f"Failed to delete file {file_path}: {e}")
        return False
