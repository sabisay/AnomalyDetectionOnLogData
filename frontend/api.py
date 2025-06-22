import sys
import os
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flask import Flask, request, jsonify, Response
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
        # temp_uploaded dosyasını otomatik tespit et
        for ext in [".csv", ".xlsx"]:
            input_path = os.path.abspath(f"temp_uploaded{ext}")
            if os.path.exists(input_path):
                break
        else:
            return jsonify({"error": "No uploaded file found in temp."}), 400

        model_path = os.path.abspath("ModularizedClasses/Model/autoencoder_model.keras")
        output_parquet = os.path.abspath("ModularizedClasses/ForDetecting/outputs/Test_processed.parquet")
        threshold = 0.452005

        model = load_model(model_path)

        abnormal_users = abnormal_user_detector(
            input_path=input_path,
            model=model,
            output_parquet=output_parquet,
            threshold=threshold
        )

        return Response(
            json.dumps({
                "message": f"Detection completed by {request.user['username']}",
                "abnormal_users": abnormal_users
            }, ensure_ascii=False),
            mimetype="application/json"
        )


    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)