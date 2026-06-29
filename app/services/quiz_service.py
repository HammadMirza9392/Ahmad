"""
Quiz Service
Generates AI-powered quizzes from knowledge base content.
"""


class QuizService:

    @staticmethod
    def build_quiz_prompt(subject_name, topic=None, quiz_type='mixed', num_questions=10):
        """Build a structured prompt for the AI to generate a quiz.
        quiz_type: mcq, true_false, fill_blank, short, long, mixed
        """
        type_instructions = {
            'mcq': 'Generate only Multiple Choice Questions with 4 options (A, B, C, D). Mark the correct answer.',
            'true_false': 'Generate only True/False questions. State the correct answer.',
            'fill_blank': 'Generate only Fill in the Blank questions. Provide the correct answer.',
            'short': 'Generate only Short Answer questions (2-3 sentences each). Provide model answers.',
            'long': 'Generate only Long Answer questions (paragraph-length). Provide detailed model answers.',
            'mixed': 'Generate a mix of MCQs, True/False, Fill in the Blank, and Short Answer questions.',
        }

        topic_line = f"Topic: {topic}" if topic else "Cover the most important topics."

        prompt = f"""Generate a quiz for the subject: {subject_name}
{topic_line}
Number of questions: {num_questions}

{type_instructions.get(quiz_type, type_instructions['mixed'])}

Format your response as valid JSON with this structure:
{{
    "quiz_title": "Quiz on ...",
    "questions": [
        {{
            "id": 1,
            "type": "mcq|true_false|fill_blank|short|long",
            "question": "...",
            "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
            "correct_answer": "...",
            "explanation": "..."
        }}
    ]
}}

For true_false questions, options should be ["True", "False"].
For fill_blank questions, options should be an empty list.
For short/long questions, options should be an empty list and correct_answer should contain the model answer.

Ensure all questions are academically accurate and relevant."""

        return prompt

    @staticmethod
    def build_score_prompt(quiz_data, student_answers):
        """Build a prompt to score student answers and identify weak areas."""
        prompt = f"""Score the following quiz answers and provide detailed feedback.

Quiz: {quiz_data.get('quiz_title', 'Quiz')}

Questions and Student Answers:
"""
        for i, q in enumerate(quiz_data.get('questions', [])):
            student_ans = student_answers.get(str(q['id']), 'No answer provided')
            prompt += f"""
Question {q['id']}: {q['question']}
Correct Answer: {q['correct_answer']}
Student's Answer: {student_ans}
"""

        prompt += """
Respond in valid JSON format:
{
    "total_score": <number>,
    "total_questions": <number>,
    "percentage": <number>,
    "results": [
        {
            "question_id": <number>,
            "is_correct": true/false,
            "student_answer": "...",
            "correct_answer": "...",
            "explanation": "..."
        }
    ],
    "weak_areas": ["topic1", "topic2"],
    "recommendations": "..."
}"""
        return prompt
