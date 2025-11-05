## Configuration du dépôt
### Initialisation du dépôt GIT local
```
git config --global user.name "Sebastien"
git config --global user.email"s.andres@hizkia.eu"
git init
git add .
git commit -m "Initialisation du projet analyse de sentiment"
```

### Lié le dépôt local à GitHub
```
git remote add origin https://github.com/sebo-hizkia/analyse-sentiment-api.git
git branch -M main
git push -u origin main
```

## Développement
### API
Lancement de l'API : ```uvicorn sentiment_api:app --reload --port 9000```

Test de l'API via interface automatique : http://127.0.0.1:9000/docs

### Page web de test
Lancement de l'application : ```streamlit run sentiment_streamlit.py```

