from fastapi import APIRouter, Depends, UploadFile, File
from app.core.dependencies import get_current_user
from app.utils.file_upload import save_upload_file
from app.models.user import User

router = APIRouter()


@router.post("")
async def upload_file(file: UploadFile = File(...), subfolder: str = "general", current_user: User = Depends(get_current_user)):
    result = await save_upload_file(file, subfolder=subfolder)
    return {"success": True, "file": result}
