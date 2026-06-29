"""
Voice Service
Configuration for Web Speech API (client-side STT/TTS).
Speech recognition and synthesis happen entirely in the browser.
This service provides configuration and fallback text.
"""


class VoiceService:

    # Supported languages for Web Speech API
    LANGUAGES = [
        ('en-US', 'English (US)'),
        ('en-GB', 'English (UK)'),
        ('ur-PK', 'Urdu (Pakistan)'),
    ]

    @staticmethod
    def get_tts_config():
        """Default text-to-speech settings."""
        return {
            'rate': 1.0,
            'pitch': 1.0,
            'volume': 1.0,
            'lang': 'en-US',
        }

    @staticmethod
    def get_stt_config():
        """Default speech-to-text settings."""
        return {
            'lang': 'en-US',
            'continuous': False,
            'interimResults': True,
        }
