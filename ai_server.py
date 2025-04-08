from flask import Flask, request, jsonify
import openai
import os
import json
from dotenv import load_dotenv

# טען את משתני הסביבה מקובץ .env
load_dotenv()

app = Flask(__name__)

# הגדר מפתח API - עדיף שיהיה מוגדר כמשתנה סביבה בלבד
client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])

@app.route('/generate', methods=['POST'])
def generate_text():
    data = request.json
    prompt = data.get('prompt', '')

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # או כל מודל אחר שזמין לך
            messages = [
                {
                    "role": "system",
                    "content": (
                        "אתה כותב ברכות יצירתיות, אישיות ומרגשות בעברית.\n"
                        "עליך להחזיר אך ורק אובייקט JSON בפורמט הבא:\n"
                        "{ \"title\": \"...\", \"content\": \"...\", \"signature\": \"...\" }\n"
                        # "הקפד על ההנחיות הבאות:\n"
                        # "- החזר אך ורק את אובייקט ה-JSON – ללא הסברים, תוספות או טקסט מסביב.\n"
                        "- הערכים בתוך האובייקט יהיו בעברית בלבד.\n"
                        # "- הכותרת (title) תהיה תמציתית, ברורה ומייצגת את נושא הברכה.\n"
                        # "- התוכן (content) יהיה נוסח ברכה חם, בגובה העיניים, אישי ומרגש.\n"
                        # "- החתימה (signature) תהיה בסגנון אישי: למשל 'שלך', 'באהבה', 'מאחל לך', וכדומה.\n"
                        # "- כתוב תמיד בעברית תקנית, בלי סלנג או קיצורים.\n"
                        # "- אם אינך מצליח לנסח ברכה מתאימה – החזר מחרוזת ריקה בלבד: \"\" (string ריק).\n"
                    )
                },
                {
                    "role": "user",
                    "content": f"כתוב ברכה עבור הבקשה הבאה: {prompt}"
                }
            ]
        )

        message = response.choices[0].message.content.strip()
        # נסה לנתח כ-JSON
        try:
            # print(message)
            blessing = json.loads(message)
            # blessing=jsonify(blessing)
            print(blessing)
            return blessing, 200
        except json.JSONDecodeError:
            print(f"Error decoding JSON: {message}")
            return jsonify({'text': message}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5001)
