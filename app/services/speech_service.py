import whisper
from gtts import gTTS
import tempfile
import os
import soundfile as sf
import numpy as np
from typing import Tuple

class SpeechService:
    def __init__(self):
        self.whisper_model = whisper.load_model("base")
        
    def speech_to_text(self, audio_data: bytes) -> str:
        """
        Convert speech to text using Whisper.
        
        Args:
            audio_data: Raw audio data in bytes
            
        Returns:
            str: Transcribed text
        """
        try:
            # Save audio data to temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_path = temp_file.name
                # Convert audio data to numpy array
                audio_array, sample_rate = sf.read(audio_data)
                sf.write(temp_path, audio_array, sample_rate)
            
            # Transcribe audio
            result = self.whisper_model.transcribe(temp_path)
            
            # Clean up temporary file
            os.unlink(temp_path)
            
            return result["text"].strip()
        except Exception as e:
            print(f"Error in speech-to-text conversion: {str(e)}")
            return ""
            
    def text_to_speech(self, text: str) -> Tuple[bytes, str]:
        """
        Convert text to speech using gTTS.
        
        Args:
            text: Text to convert to speech
            
        Returns:
            Tuple[bytes, str]: Audio data in bytes and content type
        """
        try:
            # Create temporary file for audio
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
                temp_path = temp_file.name
                
                # Generate speech
                tts = gTTS(text=text, lang='en')
                tts.save(temp_path)
                
                # Read the generated audio file
                with open(temp_path, 'rb') as audio_file:
                    audio_data = audio_file.read()
                
                # Clean up temporary file
                os.unlink(temp_path)
                
                return audio_data, 'audio/mpeg'
        except Exception as e:
            print(f"Error in text-to-speech conversion: {str(e)}")
            return b"", 'audio/mpeg' 