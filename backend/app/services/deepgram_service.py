from deepgram import Deepgram
from app.core.config import settings

class DeepgramService:
    def __init__(self, api_key=None):
        self.api_key = api_key or settings.DEEPGRAM_API_KEY
        self.client = Deepgram(self.api_key)
    
    async def transcribe_audio(self, audio_data, mimetype="audio/wav"):
        """
        Transcribe audio data to text using Deepgram
        """
        source = {'buffer': audio_data, 'mimetype': mimetype}
        response = await self.client.transcription.prerecorded(
            source,
            {
                'punctuate': True,
                'diarize': True,
                'model': 'nova',
            }
        )
        return response
    
    async def text_to_speech(self, text, voice="nova"):
        """
        Convert text to speech using Deepgram
        """
        # Implementation would depend on Deepgram's TTS API
        pass
