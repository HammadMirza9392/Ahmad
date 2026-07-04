"""
Prompt Builder
Constructs context-aware system prompts for AI responses.
"""
from app.models.institution import Institution


class PromptBuilder:

    @staticmethod
    def build_system_prompt(user, knowledge_context='', resource_files=None, custom_prompt=None, assignments=None):
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
            batch_name = user.student_batch.label if user.student_batch else 'N/A'
        except Exception:
            batch_name = 'N/A'
        try:
            semester_name = user.student_semester.name if user.student_semester else 'N/A'
        except Exception:
            semester_name = 'N/A'

        prompt = f"""You are an AI Learning Assistant for {inst_name}.

The institution's academic structure is hierarchical:
Department -> Program -> Batch (intake-year cohort) -> Semester -> Subject.

Student Information:
- Name: {user.full_name}
- Department: {dept_name}
- Program: {prog_name}
- Batch: {batch_name}
- Semester: {semester_name}

IMPORTANT RULES:
1. Only answer questions using the provided knowledge base below.
2. If the answer is not available in the knowledge base, say: "I do not have sufficient information about this topic. Please contact your instructor or check the college resources."
3. Never use knowledge from another semester, batch, department, or program.
4. Be helpful, accurate, and educational in your responses.
5. Format responses with clear headings, bullet points, and code blocks where appropriate.
6. If the student asks for a quiz, generate questions from the knowledge base only.
7. Keep responses concise but thorough.
8. If a student asks a structural question about the institution (e.g. "show students of
   a batch", "who teaches subject X in semester Y", "how many students in a batch") and the
   request is missing department, program, batch, or semester details needed to answer
   precisely, ask a clarifying follow-up question naming exactly which of those details you
   need (e.g. "Please select the department, program/batch, and semester.") instead of guessing.
9. If the student asks about assignments, homework, or deadlines, use the assignments list
   provided below (if present) rather than the knowledge base — it is always current.
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

        if assignments:
            prompt += "\n--- YOUR ASSIGNMENTS ---\n"
            for a in assignments:
                subj_name = a.subject.name if a.subject else 'Unknown Subject'
                teacher_name = a.teacher.full_name if a.teacher else 'Unknown Teacher'
                status = 'PAST DUE' if a.is_past_due else 'UPCOMING'
                marks = f", {a.total_marks} marks" if a.total_marks else ''
                prompt += (f"- \"{a.title}\" ({subj_name}, assigned by {teacher_name}) — "
                          f"due {a.due_date.strftime('%B %d, %Y at %H:%M')} [{status}]{marks}\n")
            prompt += ("--- END ASSIGNMENTS ---\n"
                      "\nWhen the student asks about assignments, deadlines, or what is due, answer using "
                      "the list above. Tell them they can view details and submit their work from the "
                      "Assignments section of the student portal.\n")

        return prompt

    @staticmethod
    def build_title_prompt(user_message):
        """Generate a short chat session title from the first user message."""
        return f'Generate a concise title (max 6 words) for a chat that starts with: "{user_message[:200]}". Reply with only the title, nothing else.'
