"""
Flashcard Service
Generates AI-powered flashcards from knowledge base content.
"""


class FlashcardService:

    @staticmethod
    def build_flashcard_prompt(subject_name, topic=None, num_cards=15):
        """Build a prompt for the AI to generate flashcards."""
        topic_line = f"Focus on: {topic}" if topic else "Cover the most important concepts."

        prompt = f"""Generate {num_cards} study flashcards for: {subject_name}
{topic_line}

Each flashcard should have a clear front (question/term) and back (answer/definition).
Include a mix of definitions, key concepts, formulas, and important facts.

Format your response as valid JSON:
{{
    "title": "Flashcards: {subject_name}",
    "cards": [
        {{
            "id": 1,
            "front": "What is ...?",
            "back": "...",
            "difficulty": "easy|medium|hard"
        }}
    ]
}}

Make the flashcards progressively harder. Ensure accuracy."""

        return prompt
