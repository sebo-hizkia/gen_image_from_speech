import streamlit as st
import requests
from loguru import logger
import tempfile
import sounddevice as sd
from scipy.io.wavfile import write
import numpy as np

# Configuration du logger
logger.add("logs/speech_streamlit.log", rotation="100 MB", level="INFO")

st.title("🎙️ Reconnaissance vocale (Speech-to-Text via API FastAPI)")

# Paramètres d'enregistrement
sample_rate = 16000  # recommandé pour Wav2Vec2
duration = st.slider("Durée de l'enregistrement (secondes)", 1, 10, 3)

# Enregistrement
if st.button("🎤 Enregistrer"):
    st.info("Enregistrement en cours... Parlez maintenant 🎙️")
    recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype="int16")
    sd.wait()
    st.success("✅ Enregistrement terminé !")

    # Sauvegarde temporaire en fichier .wav
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        write(tmp.name, sample_rate, recording)
        tmp_path = tmp.name

    # Lecture audio dans Streamlit
    st.audio(tmp_path, format="audio/wav")

    # Envoi au backend FastAPI
    try:
        with open(tmp_path, "rb") as f:
            files = {"file": f}
            response = requests.post("http://127.0.0.1:9000/speech_to_text/", files=files)

        if response.status_code == 200:
            transcription = response.json()["transcription"]
            st.subheader("🗣️ Transcription :")
            st.write(transcription)
            logger.info(f"Transcription : {transcription}")
        else:
            st.error(f"Erreur API : {response.text}")
            logger.error(f"Erreur API : {response.text}")

    except Exception as e:
        st.error(f"Erreur de communication avec l'API : {e}")
        logger.error(f"Erreur de communication avec l'API : {e}")
