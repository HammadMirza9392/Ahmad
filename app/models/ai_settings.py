"""
AI Settings Model
Stores AI provider configuration, encrypted API keys, and model parameters.
"""
from datetime import datetime
from app import db


class AIProvider(db.Model):
    __tablename__ = 'ai_providers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # Google Gemini, Groq, OpenRouter, etc.
    slug = db.Column(db.String(100), unique=True, nullable=False)
    provider_type = db.Column(db.String(50), nullable=False)  # gemini, groq, openrouter, huggingface, deepseek, custom

    # Credentials (encrypted)
    api_key_encrypted = db.Column(db.Text)
    api_base_url = db.Column(db.String(500))

    # Model config
    model_name = db.Column(db.String(255))
    temperature = db.Column(db.Float, default=0.7)
    top_p = db.Column(db.Float, default=0.9)
    max_tokens = db.Column(db.Integer, default=2048)
    streaming = db.Column(db.Boolean, default=True)
    timeout = db.Column(db.Integer, default=30)

    # Prompt
    default_prompt = db.Column(db.Text)

    # Status
    is_active = db.Column(db.Boolean, default=False)
    is_primary = db.Column(db.Boolean, default=False)
    is_backup = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<AIProvider {self.name}>'
