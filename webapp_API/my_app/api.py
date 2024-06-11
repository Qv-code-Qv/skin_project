import os
import numpy as np
import mlflow
from flask import Flask, request, jsonify, render_template, redirect, url_for
from werkzeug.utils import secure_filename
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image

api = Flask(__name__)

# Configuration de MLflow
MLFLOW_TRACKING_URI = "https://mlflow-jedha-app-ac2b4eb7451e.herokuapp.com/"
MODEL_RUN_ID = "495bc520d5ff42039590cc8038977981"

# Définition des classes
classes = ['chat', 'pas un chat']

# Assurez-vous que le dossier d'images existe
UPLOAD_FOLDER = 'src/upload'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Fonction pour télécharger et charger le modèle depuis une exécution MLflow
def get_model_from_mlflow(run_id):
 
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    artifact_uri = f"runs:/{run_id}/model"  # Spécifiez le chemin relatif du modèle
    model = mlflow.keras.load_model(artifact_uri)
    return model

# Chargement du modèle
model = get_model_from_mlflow(MODEL_RUN_ID)

# Fonction de prédiction
def predict(image_path):
 
    # Prétraitement de l'image
    img = image.load_img(image_path, target_size=(224, 224))
    img = image.img_to_array(img)
    img = np.expand_dims(img, axis=0)
    img = img.astype('float32') / 255.0

    # Prédiction
    prediction = model.predict(img)
    predicted_class = classes[np.argmax(prediction[0][0])]
    
     # Faire la prédiction
    return predicted_class

# Fonction pour traiter une requête d'envoi d'image
def new_predict(request):
    try:
        # Récupérer l'image envoyée
        if 'file' not in request.files:
            return jsonify({'error': 'Aucune image envoyée'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Nom de fichier invalide'}), 400

        # Enregistrer l'image temporairement
        image_path = os.path.join(UPLOAD_FOLDER, secure_filename(file.filename))
        file.save(image_path)

        # Prédire la classe de l'image
        predicted_class = predict(image_path)

        # Supprimer l'image temporaire
        os.remove(image_path)
        
        print(f"Image supprimée : {image_path}")

        # Générer la réponse JSON
        result = {'classe': predicted_class}
        return jsonify(result)

    except Exception as e:
        # Gérer les erreurs
        print(f"Erreur lors de la prédiction : {e}")
        return jsonify({'error': 'Une erreur est survenue'}), 500

# Route pour l'envoi d'une image
@api.route('/api/predict', methods=['POST'])
def predict_image():
    predicted_class = new_predict(request)
    if predicted_class is None:
        return jsonify({'error': 'Une erreur est survenue'}), 500
    return redirect(url_for('show_result', classe=predicted_class))

# Route pour afficher le résultat
@api.route('/result')
def show_result():

    predicted_class = request.args['classe']
    is_cat = predicted_class == 'chat'
    return render_template('result.html', is_cat=is_cat)

if __name__ == "__main__":
    api.run(port=5001, debug=True)
