## Configuration de l'environnement virtuel python
```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

La bibliothèque Sounddevice nécessite la bibliothèque système PortAudio :
```
sudo apt update
sudo apt install portaudio19-dev
```

## Configuration du dépôt
### Initialisation du dépôt GIT local
```
git config --global user.name "Sebastien"
git config --global user.email"s.andres@hizkia.eu"
git init
git add .
git commit -m "Initialisation du projet de générateur d'image suivant la parole"
```

### Lié le dépôt local à GitHub

Crée un Personal Access Token sur GitHub

Aller sur https://github.com/settings/tokens

Cliquer sur “Generate new token → Fine-grained token”.

Donner un nom, par exemple : token-gen-image.

Dans la section Repository access, choisir :

✅ “Only select repositories” → choisir gen_image_from_speech

Dans Permissions, cocher :

✅ Contents → Read and write

Cliquer sur Generate token.

Copier le token car GitHub ne l’affiche qu’une seule fois.

Utiliser le token lors du push suivant :

```
git branch -M main
git remote add origin https://github.com/sebo-hizkia/gen_image_from_speech.git
git push -u origin main
```

## Développement
### Dépendances
Le modèle audio local s'appui sur FFMPEG
```
sudo apt update
sudo apt install ffmpeg
```

### API
Lancement de l'API : ```uvicorn gen_image_api:app --reload --port 9000```

Test de l'API via interface automatique : http://127.0.0.1:9000/docs

Pour utiliser les modèles d'inférence Hugging Face, il faut créer un token via le lien : https://huggingface.co/settings/tokens

Créer un Fine-grained token et autoriser l'inférence.

Variable d'environement utilisable par le programme :
```
LOCAL_MODEL = True ou False # Utilisation du model local (par défaut True) ou inférence sur serveur Hugging Face (nécessite du crédit) si False
HF_TOKEN =  # Token Hugging Face
```

### Page web de test
Lancement de l'application : ```streamlit run gen_image_steamlit.py```

