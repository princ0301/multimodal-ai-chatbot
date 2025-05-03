from flask import Flask, render_template, request, jsonify, session
import os
import base64
from datetime import datetime
import json
from werkzeug.utils import secure_filename
 
from modules.audio_processing import transcribe_audio
from modules.image_processing import encode_image_to_base64
from modules.text_processing import get_user_query
from modules.gemini_response import generate_medical_response
from modules.reminder_scheduler import add_reminder

app = Flask(__name__)
#app.secret_key = os.urandom(24)   
 
# UPLOAD_FOLDER = 'uploads'
# if not os.path.exists(UPLOAD_FOLDER):
#     os.makedirs(UPLOAD_FOLDER)
UPLOAD_FOLDER = '/tmp/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send_message', methods=['POST'])
def send_message(): 
    if 'chat_history' not in session:
        session['chat_history'] = []
     
    user_message = request.form.get('message', '')
    tone = request.form.get('tone', 'Friendly and Simple')
     
    audio_file = request.files.get('audio')
    transcribed_text = None
    if audio_file and audio_file.filename:
        audio_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(audio_file.filename))
        audio_file.save(audio_path)
        transcribed_text = transcribe_audio(audio_path)
     
    image_file = request.files.get('image')
    image_base64 = None
    if image_file and image_file.filename:
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(image_file.filename))
        image_file.save(image_path)
        image_base64 = encode_image_to_base64(image_path)
    
    query = get_user_query(user_message, transcribed_text)
     
    tone_instruction = f"(Respond in a '{tone}' tone)\n"
    full_query = tone_instruction + query
     
    chat_history = session['chat_history']
    chat_history.append({"role": "user", "content": query})
     
    ai_response = generate_medical_response(full_query, image_base64=image_base64, history=chat_history)
  
    chat_history.append({"role": "assistant", "content": ai_response})
    session['chat_history'] = chat_history
     
    return jsonify({
        "user_message": query,
        "ai_response": ai_response,
        "transcribed_text": transcribed_text
    })

@app.route('/create_reminder', methods=['POST'])
def create_reminder():
    subject = request.form.get('subject', '')
    description = request.form.get('description', '')
    email = request.form.get('email', '')
     
    date_str = request.form.get('date', '')
    time_str = request.form.get('time', '')
    
    if not subject or not date_str or not time_str or not email:
        return jsonify({"status": "error", "message": "❌ Please fill in Subject, Date, Time, and Email."})
    
    try: 
        date_parts = date_str.split('-')
        time_parts = time_str.split(':')
        
        year, month, day = map(int, date_parts)
        hour, minute = map(int, time_parts)
        
        reminder_time = datetime(year, month, day, hour, minute)
         
        full_description = f"{subject} — {description}" if description else subject
         
        add_reminder(email=email, med=full_description, time_obj=reminder_time)
        
        return jsonify({
            "status": "success", 
            "message": f"✅ Reminder set for '{subject}' at {reminder_time.strftime('%I:%M %p on %B %d, %Y')} to {email}."
        })
        
    except Exception as e:
        return jsonify({"status": "error", "message": f"❌ Failed to process date/time: {str(e)}"})

@app.route('/clear_history', methods=['POST'])
def clear_history():
    if 'chat_history' in session:
        session.pop('chat_history')
    return jsonify({"status": "success"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  
    app.run(host='0.0.0.0', port=port)