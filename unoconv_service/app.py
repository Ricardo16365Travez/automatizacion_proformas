from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import os
import subprocess

app = FastAPI()

@app.post("/convert")
async def convert_to_pdf(file: UploadFile = File(...)):
    input_path = f"/descargas/{file.filename}"
    output_path = input_path.replace(".docx", ".pdf")

    with open(input_path, "wb") as f:
        f.write(await file.read())

    result = subprocess.run(["unoconv", "-f", "pdf", input_path])
    if result.returncode != 0 or not os.path.exists(output_path):
        return {"error": "No se pudo generar el PDF"}

    return FileResponse(output_path, media_type="application/pdf")
