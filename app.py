from flask import Flask, request, jsonify
import openai
import os
import json
import re
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
# client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])
openai.api_key = os.environ["OPENAI_API_KEY"]

@app.route('/', methods=['GET'])
def index():
    return 'שרת Flask רץ בהצלחה על פורט 5001', 200

@app.route('/generate', methods=['POST'])
def generate_text():
    data = request.json
    prompt = data.get('Prompt', '')
    style = data.get('Style', 'ידידותי')
    rhyming = data.get('Rhyming', False)
    length = data.get('Length', 'קצר')
    recipient_gender = data.get('RecipientGender', 'לא מוגדר')
    important_words = data.get('ImportantWords', [])

    instruction = (
        "אתה כותב ברכות יצירתיות, אישיות ומרגשות בעברית.\n"
        "החזר אך ורק אובייקט JSON בפורמט הבא:\n"
        "{ \"title\": \"...\", \"content\": \"...\", \"signature\": \"...\" }\n"
        "אין להוסיף טקסט נוסף או הסברים מחוץ לאובייקט.\n"
        "- הכותרת (title) צריכה להיות תמציתית וברורה.\n"
        "- התוכן (content) יהיה נוסח ברכה חם, אישי ומרגש.\n"
        "- החתימה (signature) תהיה סיום אישי ומכבד כמו 'שלך', 'באהבה', 'מאחל לך' וכו'.\n"
        "- אם אינך מצליח לנסח ברכה מתאימה – החזר מחרוזת ריקה בלבד: \"\"."
    )
    rhyming_text = "הברכה צריכה להיות מחורזת.\n" if rhyming else ""
    important_words_text = f"שלב את המילים הבאות בברכה: {', '.join(important_words)}." if important_words else ""

    user_instruction = (
         f"כתוב ברכה עבור הבקשה הבאה: {prompt}\n"
        f"סגנון הברכה: {style}.\n"
        f"{rhyming_text}"
        f"אורך הברכה: {length}.\n"
        f"הברכה מיועדת ל: {recipient_gender}.\n"
        f"{important_words_text}"
    )
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",  
            messages = [
                {
                    "role": "system",
                    "content": instruction
                },
                {
                    "role": "user",
                    "content": user_instruction
                }
            ]
        )

        message_raw = response.choices[0].message.content.strip()
        match = re.search(r'\{.*\}', message_raw, re.DOTALL)

        if match:
            message = match.group(0)
            try:
                blessing = json.loads(message)
                print(blessing)
                return blessing, 200
            except json.JSONDecodeError:
                return jsonify({'text': message_raw}), 200
        else:
            print(f"Error: No JSON object found in the response: {message_raw}")
            return jsonify({'text': message_raw}), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port)
