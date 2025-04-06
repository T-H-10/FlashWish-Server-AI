from email import message
from flask import Flask, request, jsonify
import openai
import os

app= Flask(__name__)
# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route('/generate', methods=['POST'])
def generate_text():
    data = request.json
    prompt = data.get('prompt','')
    
    try:
        response = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=[{
                "role": "user",
                "content": prompt}]
        )
        message=response.choices[0].message['content']
        return jsonify({'text': message}),200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
if __name__ == '__main__':
    app.run(port=5001)