from fastapi import FastAPI, UploadFile, File, HTTPException
from transformers import pipeline
from loguru import logger
import tempfile
import torch

# Configuration du logger
logger.add("logs/gen_image_api.log", rotation="100 MB", level="INFO")

# Création de l'application FastAPI
app = FastAPI(title="API de génération d'images")

# Device GPU ou CPU
device = 0 if torch.cuda.is_available() else -1

# Chargement du modèle Hugging Face (français)
asr_pipeline = pipeline("automatic-speech-recognition", model="facebook/wav2vec2-large-xlsr-53-french")

# Route transcription audio -> texte
@app.post("/speech_to_text/")
async def speech_to_text(file: UploadFile = File(...)):
    """
    Reçoit un fichier audio (.wav) et retourne la transcription texte.
    """
    try:
        logger.info(f"Fichier reçu : {file.filename}")

        # Sauvegarde temporaire du fichier
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        # Exécution du modèle Speech-to-Text
        result = asr_pipeline(tmp_path)
        transcription = result["text"]

        logger.info(f"Transcription : {transcription}")
        return {"transcription": transcription}

    except Exception as e:
        logger.error(f"Erreur de transcription : {e}")
        raise HTTPException(status_code=500, detail=str(e))
