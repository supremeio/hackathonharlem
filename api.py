"""Thin FastAPI prototype wrapper around Person A and Person B."""

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

from generate import generate_all, write_outputs
from intake.validator import score_intake, validate_intake

PROJECT_ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = (PROJECT_ROOT / "output").resolve()

app = FastAPI(title="Maverx Training Builder Prototype")


@app.post("/generate")
def generate(intake: dict) -> dict:
    issues = validate_intake(intake)
    score, breakdown = score_intake(intake)
    if issues:
        raise HTTPException(
            status_code=422,
            detail={"issues": issues, "score": score, "breakdown": breakdown},
        )
    if score < 80:
        raise HTTPException(
            status_code=422,
            detail={"score": score, "breakdown": breakdown},
        )

    outputs = generate_all(intake)
    paths = write_outputs(outputs, OUTPUT_DIR)
    return {
        "files": [path.name for path in paths],
        "output_dir": str(OUTPUT_DIR),
        "score": score,
        "slide_count_per_level": 20,
    }


@app.get("/download/{filename}")
def download(filename: str) -> FileResponse:
    if Path(filename).name != filename:
        raise HTTPException(status_code=404, detail="File not found.")
    path = (OUTPUT_DIR / filename).resolve()
    if path.parent != OUTPUT_DIR or not path.is_file():
        raise HTTPException(status_code=404, detail="File not found.")
    return FileResponse(path)


@app.get("/status")
def status() -> dict:
    files = sorted(path.name for path in OUTPUT_DIR.glob("*.json")) if OUTPUT_DIR.exists() else []
    return {"ready": bool(files), "files": files}
