import speech_recognition as sr
import google.generativeai as genai
from flask import Flask, request, jsonify
from io import BytesIO   
from flask_cors import CORS
from pydub import AudioSegment 

app = Flask(__name__)   # Flask constructor 
CORS(app, resources={r"/api/*": {"origins": "*"}})
app.config['MAX_CONTENT_LENGTH'] = 16*1024*1024
  
    
recognizer = sr.Recognizer()
@app.route("/")
def start():
    return "server running"
  
def mpconv(audio):
    new_audio = AudioSegment.from_mp3(audio)
    wav_io = BytesIO()
    new_audio.export(wav_io, format="wav")
    wav_io.seek(0)
    return wav_io
def convert_voice_to_text(audio):    
    try:
        text_hi = recognizer.recognize_google(audio, language="hi-IN")
        text_en = recognizer.recognize_google(audio, language="en-IN")
        print("You said (Hindi): " + text_hi)
        print("You said (English): " + text_en)
    except sr.UnknownValueError:
        text_hi = ""
        text_en = ""
        print("Sorry, I didn't understand that.")
    except sr.RequestError as e:
        text_hi = ""
        text_en = ""
        print(f"Error; {e}")
    return text_hi, text_en


def scam_detection(conversation_text, alert_level="medium"):
    genai.configure(api_key="AIzaSyCGx3cDeTHgIU9nw7gxZre0gPoa1wgUY_A")
    model = genai.GenerativeModel("gemini-1.5-flash")

    response = model.generate_content(
        f"Check this conversation for scams and alert if detected in one word: {conversation_text}",
        generation_config=genai.GenerationConfig(
            max_output_tokens=10,
            temperature=0.1,
        )
    )
    
    print(response.text)
    return(response.text)

@app.route('/api/mich', methods=['POST'])
def upload_audio():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    try:
        input_audio= mpconv(file)
        audio = sr.AudioFile(BytesIO(input_audio.read()))
        with audio as source:
            print("listening...")
            audio_data = recognizer.record(source)
        text_hi, text_en = convert_voice_to_text(audio_data)
        if text_en:
            resdata = scam_detection(text_en + text_hi)
            return jsonify({"result":resdata}), 200
        else:
            return jsonify({"error": "No text detected"}), 400
    except Exception as e:
        import traceback
        return jsonify({"error": str(e), "result":traceback.format_exc()}), 500
