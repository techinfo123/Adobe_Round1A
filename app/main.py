from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from extractor_llm import generate_outline  # ✅ FIXED IMPORT
import shutil
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        outline = generate_outline(temp_path)
    except Exception as e:
        os.remove(temp_path)
        return {"result": {"summary": f"❌ Error during extraction: {str(e)}"}}

    os.remove(temp_path)
    return {"result": {"summary": outline}}
