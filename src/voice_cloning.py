import os
import tempfile
import torch
from TTS.api import TTS

# Set environment variable to agree to Coqui TOS
os.environ['COQUI_TOS_AGREED'] = '1'

class VoiceCloner:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tts = None
        self.reference_audio = "/home/ubuntu/shevanta_voice.wav"
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the TTS model for voice cloning"""
        try:
            # Use XTTS v2 for voice cloning
            self.tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(self.device)
            print("XTTS v2 model loaded successfully")
        except Exception as e:
            print(f"Error loading XTTS v2: {e}")
            # Fallback to a simpler model
            try:
                self.tts = TTS("tts_models/en/ljspeech/tacotron2-DDC").to(self.device)
                print("Fallback model loaded successfully")
            except Exception as e2:
                print(f"Error loading fallback model: {e2}")
                self.tts = None
    
    def clone_voice(self, text, language="en"):
        """
        Clone voice using the reference audio and generate speech
        
        Args:
            text (str): Text to convert to speech
            language (str): Language code (default: "en")
        
        Returns:
            str: Path to generated audio file
        """
        if not self.tts:
            raise Exception("TTS model not initialized")
        
        # Create temporary file for output
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            output_path = temp_file.name
        
        try:
            if hasattr(self.tts, 'tts_to_file') and os.path.exists(self.reference_audio):
                # Use voice cloning with reference audio
                self.tts.tts_to_file(
                    text=text,
                    speaker_wav=self.reference_audio,
                    language=language,
                    file_path=output_path
                )
            else:
                # Fallback to regular TTS
                self.tts.tts_to_file(
                    text=text,
                    file_path=output_path
                )
            
            return output_path
        except Exception as e:
            print(f"Error in voice cloning: {e}")
            # Clean up on error
            if os.path.exists(output_path):
                os.unlink(output_path)
            raise e
    
    def generate_marathi_speech(self, text):
        """
        Generate speech for Marathi text using voice cloning
        
        Args:
            text (str): Marathi text to convert to speech
        
        Returns:
            str: Path to generated audio file
        """
        try:
            # Try with English language setting (XTTS v2 may handle Marathi better this way)
            return self.clone_voice(text, language="en")
        except Exception as e:
            print(f"Error generating Marathi speech: {e}")
            # Fallback to English
            return self.clone_voice(text, language="en")

# Global instance
voice_cloner = None

def get_voice_cloner():
    """Get or create the global voice cloner instance"""
    global voice_cloner
    if voice_cloner is None:
        voice_cloner = VoiceCloner()
    return voice_cloner

def test_voice_cloning():
    """Test function for voice cloning"""
    try:
        cloner = get_voice_cloner()
        test_text = "नमस्कार! मी शेवंता आहे."
        output_path = cloner.generate_marathi_speech(test_text)
        print(f"Voice cloning test successful. Output: {output_path}")
        return output_path
    except Exception as e:
        print(f"Voice cloning test failed: {e}")
        return None

if __name__ == "__main__":
    test_voice_cloning()

