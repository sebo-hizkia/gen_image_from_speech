from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from transformers import pipeline
from loguru import logger
import tempfile
import torch
import os
from huggingface_hub import InferenceClient
from io import BytesIO


# Configuration du logger
logger.add("logs/gen_image_api.log", rotation="100 MB", level="DEBUG")

# Création de l'application FastAPI
app = FastAPI(title="API de génération d'images")

# Device GPU ou CPU
device = 0 if torch.cuda.is_available() else 1

# Chargement du modèle Hugging Face (français) en local
asr_pipeline = pipeline("automatic-speech-recognition", model="facebook/wav2vec2-large-xlsr-53-french") # A tester : openai/whisper-small

# Pour l'inférence via les serveurs Hugging Face
HF_TOKEN = os.environ.get("HF_TOKEN")  # token stocké en variable d'environement
client = InferenceClient(api_key=HF_TOKEN, provider="hf-inference")



# Route transcription audio -> texte
@app.post("/speech_to_text/")
async def speech_to_text(file: UploadFile = File(...)):
    """
    Reçoit un fichier audio (.wav) et retourne la transcription texte.
    """
    try:
        logger.info(f"Fichier reçu : {file.filename}")

         # On passe par un fichier temporaire
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        # Exécution du modèle Speech-to-Text en local si GPU ou via serveur Hugging Face (online) sinon
        if device >= 0: # GPU disponible sur machine locale
            logger.info("Utilisation du modèle local (wav2vec2)")
            result = asr_pipeline(tmp_path)
            transcription = result.get("text", "")
        else: # Pas de GPU disponible en local
            logger.info("Utilisation de l'API Hugging Face (Whisper small)")
            result = client.automatic_speech_recognition(audio=tmp_path, model="openai/whisper-large-v3") # Utilisation du modèle Whisper d'OpenAI
            logger.debug(f"Type de résultat : {type(result)} | Contenu brut : {result}")
            transcription = result.text  # AutomaticSpeechRecognitionOutput

        logger.info(f"Transcription : {transcription}")
        return {"transcription": transcription}

    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        logger.error(f"Erreur de transcription : {e}\nTraceback:\n{tb}")
        raise HTTPException(status_code=502, detail=str(e))

class PromptRequest(BaseModel):
    prompt: str

# Route génération d'image à partir du texte
@app.post("/generate_image/")
async def generate_image(req: PromptRequest):
    """
    Reçoit un texte (prompt) et retourne une image générée.
    """
    try:
        prompt = req.prompt

        if not prompt.strip():
            raise HTTPException(status_code=400, detail="Prompt vide : rien à générer")

        logger.info(f"Génération d'image pour le prompt : {prompt}")

        # Génération via l’API Hugging Face (mode hébergé)
        image = client.text_to_image(
            prompt=prompt,
            model="black-forest-labs/FLUX.1-dev"
        )

        # Convertit l'image PIL en flux binaire
        buf = BytesIO()
        image.save(buf, format="PNG")
        buf.seek(0)

        logger.info("Image générée avec succès.")
        return StreamingResponse(buf, media_type="image/png")

    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        logger.error(f"Erreur de génération d'image : {e}\nTraceback:\n{tb}")
        raise HTTPException(status_code=500, detail=str(e))
