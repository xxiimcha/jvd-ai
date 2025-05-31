from flask import Flask, request, jsonify
from flask_cors import CORS
from chatbot_engine import generate_response

app = Flask(__name__)
CORS(app)

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")
    response = generate_response(user_message)
    return jsonify(response)

if __name__ == "__main__":
    app.run(debug=True)
