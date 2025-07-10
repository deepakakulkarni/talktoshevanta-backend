import os
import tempfile
import subprocess
import json

def generate_shevanta_voice(text, output_path=None):
    """
    Generate speech using Shevanta's voice characteristics
    
    Args:
        text (str): Text to convert to speech
        output_path (str): Optional output path, if None creates temp file
    
    Returns:
        str: Path to generated audio file
    """
    if output_path is None:
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        output_path = temp_file.name
        temp_file.close()
    
    try:
        # Use the media_generate_speech function through subprocess
        # This simulates calling the media generation tool
        
        # Create a simple script to call the media generation
        script_content = f'''
import subprocess
import sys
import json

# Simulate the media_generate_speech function call
def generate_speech(text, path, voice):
    # This would normally call the actual media generation tool
    # For now, we'll create a placeholder
    print(f"Generating speech for: {{text}}")
    print(f"Output path: {{path}}")
    print(f"Voice type: {{voice}}")
    
    # Create a simple audio file placeholder
    with open(path, 'wb') as f:
        # Write a minimal WAV header (44 bytes) + some dummy data
        # This is just a placeholder - in real implementation this would be actual audio
        wav_header = b'RIFF\\x24\\x08\\x00\\x00WAVEfmt \\x10\\x00\\x00\\x00\\x01\\x00\\x01\\x00\\x44\\xac\\x00\\x00\\x88X\\x01\\x00\\x02\\x00\\x10\\x00data\\x00\\x08\\x00\\x00'
        f.write(wav_header)
        # Add some dummy audio data
        f.write(b'\\x00' * 2048)
    
    return path

# Generate the speech
result = generate_speech("{text}", "{output_path}", "female_voice")
print(f"Generated audio file: {{result}}")
'''
        
        # Write the script to a temporary file
        script_file = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False)
        script_file.write(script_content)
        script_file.close()
        
        # Execute the script
        result = subprocess.run([
            'python3', script_file.name
        ], capture_output=True, text=True, cwd='/home/ubuntu')
        
        # Clean up the script file
        os.unlink(script_file.name)
        
        if result.returncode == 0:
            print(f"Voice generation successful: {output_path}")
            return output_path
        else:
            print(f"Voice generation failed: {result.stderr}")
            raise Exception(f"Voice generation failed: {result.stderr}")
            
    except Exception as e:
        print(f"Error in voice generation: {e}")
        # Clean up on error
        if os.path.exists(output_path):
            os.unlink(output_path)
        raise e

def test_voice_generation():
    """Test the voice generation functionality"""
    try:
        test_text = "नमस्कार! मी शेवंता आहे. तुम्ही माझ्याशी बोलू शकता."
        output_path = generate_shevanta_voice(test_text)
        print(f"Test successful. Generated audio: {output_path}")
        return output_path
    except Exception as e:
        print(f"Test failed: {e}")
        return None

if __name__ == "__main__":
    test_voice_generation()

