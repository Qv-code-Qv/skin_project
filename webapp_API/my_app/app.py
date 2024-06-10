from flask import Flask, render_template
from dotenv import load_dotenv
import os
from flask_cors import CORS

load_dotenv()  # Charger les variables d'environnement à partir du fichier .env

app = Flask(__name__)


@app.route('/')
def home():
    base_url = os.getenv('APP_URL')  # Valeur par défaut si la variable n'est pas définie
    api_url = os.getenv('API_URL')  # Valeur par défaut si la variable n'est pas définie
    is_cat = True  # Remplacez ceci par votre logique réelle
    return render_template('index.html', is_cat=is_cat, base_url=base_url, api_url=api_url)

if __name__ == "__main__":
    app.run(port=5000, debug=True)
