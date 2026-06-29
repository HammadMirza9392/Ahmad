"""
AI Service
High-level interface for AI operations used by controllers and routes.
Manages provider CRUD and delegates chat to ContextManager.
"""
from app import db
from app.models.ai_settings import AIProvider
from app.utils.encryption import encrypt_value, decrypt_value
from app.ai.provider_factory import get_all_provider_types, _build_provider


class AIService:

    @staticmethod
    def get_all_providers():
        return AIProvider.query.order_by(AIProvider.name).all()

    @staticmethod
    def get_provider_by_id(provider_id):
        return db.session.get(AIProvider, provider_id)

    @staticmethod
    def get_primary_provider():
        return AIProvider.query.filter_by(is_primary=True, is_active=True).first()

    @staticmethod
    def create_provider(data):
        provider = AIProvider(
            name=data['name'],
            slug=data['slug'],
            provider_type=data['provider_type'],
            api_key_encrypted=encrypt_value(data.get('api_key', '')),
            api_base_url=data.get('api_base_url'),
            model_name=data.get('model_name'),
            temperature=float(data.get('temperature', 0.7)),
            top_p=float(data.get('top_p', 0.9)),
            max_tokens=int(data.get('max_tokens', 2048)),
            streaming=data.get('streaming', True),
            timeout=int(data.get('timeout', 30)),
            default_prompt=data.get('default_prompt'),
            is_active=data.get('is_active', False),
            is_primary=data.get('is_primary', False),
            is_backup=data.get('is_backup', False),
        )
        # Enforce single primary
        if provider.is_primary:
            AIProvider.query.filter(AIProvider.id != provider.id).update({'is_primary': False})
        if provider.is_backup:
            AIProvider.query.filter(AIProvider.id != provider.id).update({'is_backup': False})

        db.session.add(provider)
        db.session.commit()
        return provider

    @staticmethod
    def update_provider(provider, data):
        for field in ['name', 'provider_type', 'api_base_url', 'model_name',
                       'default_prompt', 'streaming']:
            if field in data:
                setattr(provider, field, data[field])

        if 'api_key' in data and data['api_key']:
            provider.api_key_encrypted = encrypt_value(data['api_key'])

        for num_field in [('temperature', float), ('top_p', float), ('max_tokens', int), ('timeout', int)]:
            if num_field[0] in data:
                setattr(provider, num_field[0], num_field[1](data[num_field[0]]))

        if 'is_active' in data:
            provider.is_active = data['is_active']
        if data.get('is_primary'):
            AIProvider.query.filter(AIProvider.id != provider.id).update({'is_primary': False})
            provider.is_primary = True
        if data.get('is_backup'):
            AIProvider.query.filter(AIProvider.id != provider.id).update({'is_backup': False})
            provider.is_backup = True

        db.session.commit()
        return provider

    @staticmethod
    def delete_provider(provider):
        db.session.delete(provider)
        db.session.commit()

    @staticmethod
    def test_provider(provider_id):
        """Test an AI provider's connection. Returns (success, message)."""
        record = db.session.get(AIProvider, provider_id)
        if not record:
            return False, 'Provider not found.'
        try:
            instance = _build_provider(record)
            return instance.test_connection()
        except Exception as e:
            return False, str(e)

    @staticmethod
    def get_decrypted_key(provider):
        """Get decrypted API key (for display masking)."""
        key = decrypt_value(provider.api_key_encrypted)
        if not key:
            return ''
        # Mask for display: show first 4 and last 4 chars
        if len(key) > 8:
            return key[:4] + '*' * (len(key) - 8) + key[-4:]
        return '****'

    @staticmethod
    def get_provider_types():
        return get_all_provider_types()
