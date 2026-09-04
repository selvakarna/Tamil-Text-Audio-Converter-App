from flask import Flask, render_template, request, jsonify, send_file
import easyocr
import os
from googletrans import Translator
from gtts import gTTS
import tempfile
import uuid

app = Flask(__name__)

# Initialize EasyOCR reader (supports Hindi, Tamil, Telugu, Kannada, Malayalam, English)
reader = easyocr.Reader(['en', 'hi', 'ta', 'te', 'kn', 'ml'])

# Initialize translator
translator = Translator()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'})

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'})

    # Save uploaded file
    temp_path = os.path.join(tempfile.gettempdir(), f"{uuid.uuid4()}.jpg")
    file.save(temp_path)

    # OCR: Extract text
    results = reader.readtext(temp_path, detail=0)
    detected_text = ' '.join(results)

    if not detected_text:
        return jsonify({'error': 'No text detected in image'})

    # Translate to Tamil
    try:
        translation = translator.translate(detected_text, src='auto', dest='ta')
        tamil_text = translation.text
    except Exception as e:
        return jsonify({'error': f'Translation failed: {str(e)}'})

    # Generate audio
    try:
        tts = gTTS(text=tamil_text, lang='ta', slow=False)
        audio_path = os.path.join(tempfile.gettempdir(), f"{uuid.uuid4()}.mp3")
        tts.save(audio_path)
    except Exception as e:
        return jsonify({'error': f'Audio generation failed: {str(e)}'})

    # Clean up temp files
    os.remove(temp_path)

    return jsonify({
        'original_text': detected_text,
        'tamil_text': tamil_text,
        'audio_path': audio_path
    })

@app.route('/download/<filename>')
def download_file(filename):
    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
