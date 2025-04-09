from flask import Flask, request, jsonify
import openai
import os
import json
import re
from dotenv import load_dotenv
# טען את משתני הסביבה מקובץ .env
load_dotenv()

app = Flask(__name__)

# הגדר מפתח API - עדיף שיהיה מוגדר כמשתנה סביבה בלבד
client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])

@app.route('/generate', methods=['POST'])
def generate_text():
    data = request.json
    print("------")
    print(data)
    print("------")
    # קח את הפרמטרים מהבקשה
    prompt = data.get('Prompt', '')
    style = data.get('Style', 'ידידותי')
    rhyming = data.get('Rhyming', False)
    length = data.get('Length', 'קצר')
    recipient_gender = data.get('RecipientGender', 'לא מוגדר')
    important_words = data.get('ImportantWords', [])

     # בניית ההנחיה למודל
    instruction = (
        "אתה כותב ברכות יצירתיות, אישיות ומרגשות בעברית.\n"
        "החזר אך ורק אובייקט JSON בפורמט הבא:\n"
        "{ \"title\": \"...\", \"content\": \"...\", \"signature\": \"...\" }\n"
        "אין להוסיף טקסט נוסף או הסברים מחוץ לאובייקט.\n"
        "- הכותרת (title) צריכה להיות תמציתית וברורה.\n"
        "- התוכן (content) יהיה נוסח ברכה חם, אישי ומרגש.\n"
        "- החתימה (signature) תהיה סיום אישי ומכבד כמו 'שלך', 'באהבה', 'מאחל לך' וכו'.\n"
        "- אם אינך מצליח לנסח ברכה מתאימה – החזר מחרוזת ריקה בלבד: \"\".\n"
    )

    # בקשת המשתמש
    user_instruction = (
        f"כתוב ברכה עבור הבקשה הבאה: {prompt}\n"
        f"סגנון הברכה: {style}.\n"
        f"{'הברכה צריכה להיות מחורזת.\n' if rhyming else ''}"
        f"אורך הברכה: {length}.\n"
        f"הברכה מיועדת ל: {recipient_gender}.\n"
        f"{'שלב את המילים הבאות בברכה: ' + ', '.join(important_words) + '.' if important_words else ''}"
    )
    print("------\n-----------")
    print(user_instruction)
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # או כל מודל אחר שזמין לך
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

        # message = response.choices[0].message.content.strip()
        
        # ננסה לחלץ את האובייקט JSON מהטקסט כולו
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
            return jsonify({'text': message_raw}), 200
        
        # # נסה לנתח כ-JSON
        # try:
        #     # print(message)
        #     blessing = json.loads(message)
        #     # blessing=jsonify(blessing)
        #     print(blessing)
        #     return blessing, 200
        # except json.JSONDecodeError:
        #     print(f"Error decoding JSON: {message}")
        #     return jsonify({'text': message}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5001)
