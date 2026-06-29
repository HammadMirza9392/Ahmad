"""
Prompt Builder
Constructs context-aware system prompts for AI responses.
"""
from app.models.institution import Institution


class PromptBuilder:

    @staticmethod
    def build_system_prompt(user, knowledge_context='', resource_files=None, custom_prompt=None):
        """Build the full system prompt injected into every AI call.
        Includes institution info, student context, knowledge base, and resource links.
        """
        institution = Institution.query.first()
        inst_name = institution.name if institution else 'the institution'

        # Student academic context (use try/except for detached session safety)
        try:
            dept_name = user.department.name if user.department else 'N/A'
        except Exception:
            dept_name = 'N/A'
        try:
            prog_name = user.program.name if user.program else 'N/A'
        except Exception:
            prog_name = 'N/A'
        try:
            class_name = user.student_class.name if user.student_class else 'N/A'
        except Exception:
            class_name = 'N/A'

        prompt = f"""You are an AI Learning Assistant for {inst_name}.

Student Information:
- Name: {user.full_name}
- Department: {dept_name}
- Program: {prog_name}
- Class: {class_name}
- Semester: {user.semester or 'N/A'}

IMPORTANT RULES:
1. Only answer questions using the provided knowledge base below.
2. If the answer is not available in the knowledge base, say: "I do not have sufficient information about this topic. Please contact your instructor or check the college resources."
3. Never use knowledge from another class, department, or program.
4. Be helpful, accurate, and educational in your responses.
5. Format responses with clear headings, bullet points, and code blocks where appropriate.
6. If the student asks for a quiz, generate questions from the knowledge base only.
7. Keep responses concise but thorough.
"""

        if custom_prompt:
            prompt += f"\nAdditional Instructions:\n{custom_prompt}\n"

        if knowledge_context:
            prompt += f"\n--- KNOWLEDGE BASE ---\n{knowledge_context}\n--- END KNOWLEDGE BASE ---\n"

        if resource_files:
            prompt += "\n--- AVAILABLE RESOURCES ---\n"
            for f in resource_files:
                prompt += f"- {f['name']} (Type: {f['type']}, File: {f['filename']})\n"
            prompt += "--- END RESOURCES ---\n"
            prompt += "\nWhen mentioning resources, tell the student they can download them from the Downloads section.\n"

        return prompt

    @staticmethod
    def build_title_prompt(user_message):
        """Generate a short chat session title from the first user message."""
        return f'Generate a concise title (max 6 words) for a chat that starts with: "{user_message[:200]}". Reply with only the title, nothing else.'
