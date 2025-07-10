from flask import Blueprint, request, jsonify, send_file
from flask_cors import cross_origin
import os
import tempfile
import speech_recognition as sr
from io import BytesIO

voice_bp = Blueprint('voice', __name__)

def generate_shevanta_speech(text):
    """Generate speech using Shevanta's voice"""
    try:
        # Create temporary file for audio output
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        output_path = temp_file.name
        temp_file.close()
        
        # Import and use the media generation function
        import sys
        sys.path.append('/home/ubuntu')
        
        # Use the media_generate_speech function
        from media_generate_speech import media_generate_speech
        
        # Generate speech with female voice (closest to Shevanta's characteristics)
        media_generate_speech(
            brief="Generating Shevanta voice response",
            path=output_path,
            text=text,
            voice="female_voice"
        )
        
        return output_path
        
    except Exception as e:
        print(f"Error generating speech: {e}")
        # Fallback: create a simple placeholder file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        temp_file.close()
        return temp_file.name

@voice_bp.route('/process-voice', methods=['POST'])
@cross_origin()
def process_voice():
    try:
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
        
        audio_file = request.files['audio']
        
        # Save the uploaded audio to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_audio:
            audio_file.save(temp_audio.name)
            
            # Initialize speech recognition
            recognizer = sr.Recognizer()
            
            # Convert audio to text
            with sr.AudioFile(temp_audio.name) as source:
                audio_data = recognizer.record(source)
                try:
                    # Try Marathi first, then English
                    text = recognizer.recognize_google(audio_data, language='mr-IN')
                except sr.UnknownValueError:
                    try:
                        text = recognizer.recognize_google(audio_data, language='en-IN')
                    except sr.UnknownValueError:
                        return jsonify({'error': 'Could not understand audio'}), 400
                except sr.RequestError as e:
                    return jsonify({'error': f'Speech recognition error: {str(e)}'}), 500
            
            # Clean up temporary file
            os.unlink(temp_audio.name)
        
        # Generate response based on input
        response_text = generate_response(text)
        
        # Generate speech for the response
        audio_path = generate_shevanta_speech(response_text)
        
        return jsonify({
            'transcript': text,
            'response': response_text,
            'audio_url': f'/api/get-audio/{os.path.basename(audio_path)}'
        })
        
    except Exception as e:
        return jsonify({'error': f'Processing error: {str(e)}'}), 500

@voice_bp.route('/process-text', methods=['POST'])
@cross_origin()
def process_text():
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': 'No text provided'}), 400
        
        text = data['text']
        
        # Generate response based on input
        response_text = generate_response(text)
        
        # Generate speech for the response
        audio_path = generate_shevanta_speech(response_text)
        
        return jsonify({
            'transcript': text,
            'response': response_text,
            'audio_url': f'/api/get-audio/{os.path.basename(audio_path)}'
        })
        
    except Exception as e:
        return jsonify({'error': f'Processing error: {str(e)}'}), 500

@voice_bp.route('/generate-speech', methods=['POST'])
@cross_origin()
def generate_speech():
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': 'No text provided'}), 400
        
        text = data['text']
        
        # Generate speech using Shevanta's voice
        audio_path = generate_shevanta_speech(text)
        
        return jsonify({
            'message': 'Speech generated successfully',
            'audio_url': f'/api/get-audio/{os.path.basename(audio_path)}',
            'text': text
        })
        
    except Exception as e:
        return jsonify({'error': f'TTS error: {str(e)}'}), 500

@voice_bp.route('/get-audio/<filename>')
@cross_origin()
def get_audio(filename):
    """Serve generated audio files"""
    try:
        # Look for the file in temp directory
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, filename)
        
        if os.path.exists(file_path):
            return send_file(file_path, mimetype='audio/wav')
        else:
            return jsonify({'error': 'Audio file not found'}), 404
    except Exception as e:
        return jsonify({'error': f'Error serving audio: {str(e)}'}), 500

def generate_response(input_text):
    """Generate chatbot response based on input text"""
    lower_input = input_text.lower()
    
    if any(word in lower_input for word in ['नमस्कार', 'हॅलो', 'hello', 'hi']):
        return "नमस्कार! मी शेवंता आहे. तुम्हाला कसे मदत करू शकते?"
    elif any(word in lower_input for word in ['तुझे नाव', 'name', 'नाव']):
        return "माझे नाव शेवंता आहे. मी एक आवाज सहाय्यक आहे."
    elif any(word in lower_input for word in ['कसे आहेस', 'how are you', 'कसे']):
        return "मी ठीक आहे, धन्यवाद! तुम्ही कसे आहात?"
    elif any(word in lower_input for word in ['धन्यवाद', 'thank you', 'thanks']):
        return "तुमचे स्वागत आहे! मला तुमची मदत करून आनंद झाला."
    elif any(word in lower_input for word in ['बाय', 'bye', 'goodbye']):
        return "अलविदा! पुन्हा भेटूया!"
    elif any(word in lower_input for word in ['time', 'वेळ']):
        return "मला वेळ माहित नाही, पण मी तुम्हाला मदत करू शकते."
    elif any(word in lower_input for word in ['weather', 'हवामान']):
        return "मला हवामानाची माहिती नाही, पण तुम्ही बाहेर पाहू शकता."
    elif any(word in lower_input for word in ['तू कोण', 'who are you', 'कोण']):
        return "मी शेवंता आहे, तुमची आवाज सहाय्यक. मी तुम्हाला मराठी आणि इंग्रजीमध्ये मदत करू शकते."
    elif any(word in lower_input for word in ['काय करतेस', 'what do you do', 'काय']):
        return "मी तुमच्याशी बोलू शकते आणि तुमच्या प्रश्नांची उत्तरे देऊ शकते. तुम्ही मला काहीही विचारू शकता."
    else:
        return "मला समजले. तुम्ही आणखी काही विचारू शकता."

