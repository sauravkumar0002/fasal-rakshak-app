import os
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
from dotenv import load_dotenv

# 1. Setup Application
load_dotenv()
app = Flask(__name__, template_folder='templates')

# 2. Configure Gemini AI (Get key from Google AI Studio)
# For local testing, you can hardcode it here, but for deployment use env vars
GOOGLE_API_KEY = "AIzaSyCATTL5gI6OUxNnZlZoZFRLlA5VAw9-yIc"
genai.configure(api_key=GOOGLE_API_KEY)

model = genai.GenerativeModel('gemini-1.5-flash')

# 3. Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_crop():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No image uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        # Read image
        image_data = file.read()
        
        # AI Prompt
        prompt = """
        You are an expert plant pathologist. Analyze this crop image.
        Return a strict JSON object (NO markdown) with these fields:
        {
            "disease": "Name of disease or 'Healthy'",
            "confidence": 95,
            "treatment": "One specific chemical or organic treatment.",
            "prevention": "One tip to prevent it next time."
        }
        """

        response = model.generate_content([
            {'mime_type': file.content_type, 'data': image_data},
            prompt
        ])

        # Clean response
        clean_text = response.text.replace('```json', '').replace('```', '').strip()
        return clean_text, 200, {'Content-Type': 'application/json'}

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)