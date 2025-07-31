from fastapi import APIRouter, UploadFile, File
from api.service import process_pdf

router = APIRouter()

@router.post("/extract")
async def extract_pdf(file: UploadFile = File(...)):
    result = await process_pdf(file)
    return result
