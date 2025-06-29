from flask import Flask, render_template, request, jsonify
import openai
import os
from database_manager import init_db, update_database
from chat import get_response

app = Flask(__name__)

# Load API key from environment variable
openai.api_key = "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"
if not openai.api_key:
    raise ValueError("OPENAI_API_KEY environment variable is not set")

# Initialize database
init_db()

@app.get("/")
def index_get():
    return render_template("base.html")

@app.post("/predict")
def predict():
    try:
        text = request.get_json().get("message")
        if not text:
            return jsonify({"error": "Message not provided."}), 400
        
        if len(text) > 1000:  # Add reasonable message length limit
            return jsonify({"error": "Message too long. Maximum length is 1000 characters."}), 400

        user_id = request.headers.get('X-User-ID', 'default_user')
        response = get_response(text, user_id)
        update_database(text, response)

        return jsonify({"answer": response})
    except Exception as e:
        app.logger.error(f"Error in predict endpoint: {str(e)}")
        return jsonify({"error": "An internal error occurred"}), 500

@app.post("/query")
def query():
    try:
        data = request.get_json()
        user_query = data.get("message")

        if not user_query:
            return jsonify({"error": "Query not provided."}), 400

        if len(user_query) > 1000:
            return jsonify({"error": "Query too long. Maximum length is 1000 characters."}), 400

        user_id = request.headers.get('X-User-ID', 'default_user')
        response = get_response(user_query, user_id)
        return jsonify({"answer": response})
    except Exception as e:
        app.logger.error(f"Error in query endpoint: {str(e)}")
        return jsonify({"error": "An internal error occurred"}), 500

@app.get("/welcome")
def welcome():
    return jsonify({"message": "Welcome to the Chatbot! How can I assist you today?"})

@app.get("/initialize")
def initialize():
    return jsonify({"answer": "Welcome to the Chatbot! How can I assist you today?"})

if __name__ == "__main__":
    app.run(debug=True)