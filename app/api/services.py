import shutil
from pathlib import Path
from app.extractor_llm import generate_outline

async def process_pdf(file):
    input_path = Path("app/input") / file.filename
    with open(input_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    result = generate_outline(str(input_path))
    return result
