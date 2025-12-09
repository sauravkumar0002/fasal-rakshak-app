import os
import json
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
from dotenv import load_dotenv

# 1. Setup Application
load_dotenv()
app = Flask(__name__, template_folder='templates')

# 2. Configure Gemini AI (Get key from Google AI Studio)
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "AIzaSyCATTL5gl6OUxNnZlZoZFRLlA5VAw9-ylc")
genai.configure(api_key=GOOGLE_API_KEY)

model = genai.GenerativeModel('gemini-1.0')

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
        
        # Get mime type
        mime_type = file.content_type or 'image/jpeg'
        
        # AI Prompt
        prompt = """
        You are an expert plant pathologist. Analyze this crop image.
        Return ONLY a valid JSON object (no markdown, no code blocks) with these exact fields:
        {
            "disease": "Name of disease or 'Healthy'",
            "confidence": 85,
            "treatment": "One specific chemical or organic treatment.",
            "prevention": "One tip to prevent it next time."
        }
        """

        # Create image part for Gemini
        image_part = {
            'mime_type': mime_type,
            'data': image_data
        }

        response = model.generate_content([image_part, prompt])
        
        # Clean response - remove any markdown formatting
        response_text = response.text.strip()
        response_text = response_text.replace('```json', '').replace('```', '').strip()
        
        # Parse to validate JSON and return
        parsed_response = json.loads(response_text)
        return jsonify(parsed_response)

    except json.JSONDecodeError as e:
        app.logger.error(f"JSON Parse Error: {e}, Response: {response_text}")
        return jsonify({
            'disease': 'Analysis Error',
            'confidence': 0,
            'treatment': 'Could not parse AI response. Please try again.',
            'prevention': 'Try uploading a clearer image.'
        }), 200
    except Exception as e:
        app.logger.error(f"Error in analyze: {str(e)}")
        return jsonify({
            'disease': 'Error',
            'confidence': 0,
            'treatment': str(e),
            'prevention': 'Please check your API key and try again.'
        }), 500

if __name__ == '__main__':
    app.run(debug=True)