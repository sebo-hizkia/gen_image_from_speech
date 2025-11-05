import streamlit as st
import requests
from loguru import logger
import tempfile
import sounddevice as sd
from scipy.io.wavfile import write
import numpy as np

# Configuration du logger
logger.add("logs/speech_streamlit.log", rotation="100 MB", level="INFO")

st.set_page_config(page_title="Speech-to-Image", page_icon="🎨")
st.title("🎙️ Générateur d'image à la voix")

API_URL = "http://127.0.0.1:9000"

# --- SECTION 1 : Enregistrement de la voix ---
st.header("🎤 Étape 1 : Enregistrez votre voix")

# Paramètres d'enregistrement
sample_rate = 16000  # recommandé pour Wav2Vec2
duration = st.slider("Durée de l'enregistrement (secondes)", 1, 10, 3)

# stockage persistant (pour réutiliser la transcription pour la génération d'image)
if "transcription" not in st.session_state:
    st.session_state.transcription = ""

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

    # Envoi à l'API FastAPI pour transcription
    try:
        with open(tmp_path, "rb") as f:
            files = {"file": f}
            response = requests.post(f"{API_URL}/speech_to_text/", files=files)

        if response.status_code == 200:
            st.session_state.transcription = response.json().get("transcription", "")
            st.subheader("🗣️ Transcription :")
            st.write(st.session_state.transcription)
            logger.info(f"Transcription : {st.session_state.transcription}")
        else:
            st.error(f"Erreur API (transcription) : {response.text}")
            logger.error(f"Erreur API (transcription) : {response.text}")

    except Exception as e:
        st.error(f"Erreur de communication avec l'API : {e}")
        logger.error(f"Erreur de communication avec l'API : {e}")

# --- SECTION 2 : Génération d'image ---
st.header("🎨 Étape 2 : Générez une image à partir du texte")

# Si transcription disponible, préremplir le champ texte
prompt = st.text_area(
    "Entrez un texte ou utilisez celui transcrit :",
    value=st.session_state.transcription,
    placeholder="Décrivez ce que vous souhaitez voir..."
)

if st.button("🖼️ Générer l'image"):
    if not prompt.strip():
        st.warning("Veuillez entrer un texte avant de générer une image.")
    else:
        # Envoi à l'API FastAPI pour génération de l'image
        try:
            with st.spinner("Génération en cours..."):
                response = requests.post(
                    f"{API_URL}/generate_image/",
                    json={"prompt": prompt},
                    timeout=300
                )

            if response.status_code == 200 and response.headers.get("content-type", "").startswith("image/"):
                st.image(response.content, caption=f"🎨 Image générée pour : « {prompt} »", use_column_width=True)
                logger.info(f"Image générée pour le prompt : {prompt}")
            else:
                st.error(f"Erreur API (image) : {response.text}")
                logger.error(f"Erreur API (image) : {response.text}")

        except Exception as e:
            st.error(f"Erreur de communication avec l'API d'image : {e}")
            logger.error(f"Erreur de communication avec l'API d'image : {e}")
