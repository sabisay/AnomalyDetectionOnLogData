import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flask import Flask, request, jsonify
from keras.models import load_model
from auth import generate_token, login_required
from users_db import users
from passlib.hash import bcrypt
from ModularizedClasses.ForDetecting.utils import abnormal_user_detector


app = Flask(__name__)

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    user = users.get(username)

    if not user:
        return jsonify({"error": "User not found"}), 404

    if not bcrypt.verify(password, user["password"]):
        return jsonify({"error": "Invalid password"}), 401

    token = generate_token(username, user["role"])
    return jsonify({"token": token})

@app.route("/run-detection", methods=["POST"])
@login_required(roles=["admin", "analyst"])
def run_detection():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file part in the request"}), 400

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No selected file"}), 400


        # Uzantıyı al
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in [".csv", ".xlsx"]:
            return jsonify({"error": "Unsupported file type"}), 400

        # Dosyayı proje köküne temp_uploaded.csv/xlsx olarak kaydet
        temp_input_path = os.path.abspath(f"temp_uploaded{ext}")
        file.save(temp_input_path)


 

        # Model ve threshold
        model_path = r"ModularizedClasses/Model/lstm_autoencoder_model.keras"
        output_parquet = r"ModularizedClasses/ForDetecting/outputs/Test_processed.parquet"
        threshold = 0.452005

        # Model yükle
        model = load_model(model_path)

        # Pipeline çalıştır
        abnormal_users = abnormal_user_detector(
            input_path=temp_input_path,
            model=model,
            output_parquet=output_parquet,
            threshold=threshold
        )

        return jsonify({
            "message": f"Detection completed by {request.user['username']}",
            "abnormal_users": abnormal_users
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)