from fastapi import APIRouter, UploadFile, File, HTTPException
from ai.inference_engine import get_inference_engine, InferenceResult

router = APIRouter(prefix="/vision", tags=["Vision / AI"])

@router.post("/analyze", response_model=InferenceResult)
async def analyze_image(file: UploadFile = File(...)):
    """
    Accepts an uploaded image and runs inference using the AI engine.
    Returns structured detections.
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image.")

    image_bytes = await file.read()

    engine = get_inference_engine()
    result = engine.run_on_bytes(image_bytes)

    return result
