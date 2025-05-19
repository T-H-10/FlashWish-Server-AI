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
    prompt = data.get('prompt', '')
    style = data.get('style', 'ידידותי')
    rhyming = data.get('rhyming', False)
    length = data.get('length', 'ארוך')
    recipient_gender =data.get('recipientGender', 'לא מוגדר')
    important_words = data.get('importantWords', [])

    instruction = (
        "אתה מומחה בכתיבת ברכות בעברית – יצירתיות, אישיות ומרגשות.\n"
        "המשימה שלך היא לנסח ברכה מותאמת אישית לנתוני משתמש ולהחזיר **אך ורק** אובייקט JSON תקני, בפורמט הבא\n"
        "{ \"title\": \"...\", \"content\": \"...\", \"signature\": \"...\" }\n\n"
       "שים לב להנחיות החיוניות הבאות:\n"
    "- **אין להוסיף אף טקסט אחר** מלבד האובייקט.\n"
    "- על הכותרת (title) להיות תמציתית, קליטה וברורה.\n"
    "- התוכן (content) צריך להיות ברכה חמה, אישית ומרגשת, לפי כל הנתונים שנמסרו – **ובמיוחד** לפי תוכן הבקשה המקורית.\n"
    "- החתימה (signature) תהיה סיום אישי ומכבד: למשל 'באהבה', 'שלך', 'מאחל לך מכל הלב' וכדומה.\n"
    "- אם לא ניתן לנסח ברכה – החזר אך ורק את המחרוזת הריקה: \"\" (ללא JSON).\n"
 )
    # rhyming_text = "הברכה צריכה להיות מחורזת.\n" if rhyming else ""
    important_words_text = f"שלב את המילים הבאות בתוך תוכן הברכה: {', '.join(important_words)}." if important_words else ""

    user_instruction = (
        f"אנא נסח ברכה בהתבסס על הבקשה הבאה:  {prompt}\n"
        f"סגנון הברכה: {style}.\n"
        f"אורך הברכה: {length}.\n"
        f"- מין מקבל הברכה: {recipient_gender}.\n"
        f"{'– הברכה צריכה להיות מחורזת.' if rhyming else ''}\n"
        f"{important_words_text}\n"
        f"הקפד להשתמש במידע הנ\"ל ליצירת ברכה מותאמת אישית.\n"
    )
    print(user_instruction)
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
                # print(blessing)
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
