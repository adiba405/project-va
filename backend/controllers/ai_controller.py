import os

from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from groq import Groq

from controllers.file_analyzer import extract_text_from_file
from utils.helpers import parse_object_id, resp


CONTEXTUAL_STUDY_ASSISTANT_PROMPT = (
    "You are a helpful AI study assistant.\n"
    "Use the provided study material as your primary context when it is available.\n"
    "If notes or uploaded material are provided, prioritize them in your answer.\n"
    "If the user asks about the user's real app data (e.g., 'how many tasks', 'how many notes'), you MUST only answer using numeric data provided in the prompt/context.\n"
    "If the required data is not provided, respond that you don't have access to it and tell the user what to connect (file/note) or to use the relevant dashboard section.\n"
    "- Keep answers clear, relevant, and concise unless the user asks for detail."
)


def get_ai_client():
    # Ensure .env is loaded in this module (some runners may not load it before imports)
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except Exception:
        pass

    api_key = os.getenv('GROQ_API_KEY', '').strip()
    if not api_key:
        return None
    return Groq(api_key=api_key)


def get_ai_model():
    # Groq models (example): llama3-70b-8192, llama3-8b-8192, mixtral-8x7b-32768
    # NOTE: Groq has decommissioned older llama3 variants. Use a currently supported model by default.
    # You can override via .env: GROQ_MODEL=...
    return os.getenv('GROQ_MODEL', 'llama-3.1-8b-instant').strip() or 'llama-3.1-8b-instant'


def _normalize_context_text(text):
    return ' '.join((text or '').split()).strip()


def _build_contextual_messages(message, study_material):
    return [
        {'role': 'system', 'content': CONTEXTUAL_STUDY_ASSISTANT_PROMPT},
        {
            'role': 'user',
            'content': (
                "Study material:\n"
                f"{study_material}\n\n"
                "Student question:\n"
                f"{message}"
            )
        }
    ]


def _build_general_messages(message):
    return [
        {
            'role': 'system',
            'content': 'You are a helpful academic assistant. Answer clearly and concisely.'
        },
        {'role': 'user', 'content': message}
    ]


def _build_note_context(note):
    parts = []
    subject = (note.get('subject') or '').strip()
    topic = (note.get('topic') or '').strip()
    content = (note.get('content') or '').strip()
    tags = note.get('tags') or []

    if subject:
        parts.append(f"Subject: {subject}")
    if topic:
        parts.append(f"Topic: {topic}")
    if tags:
        parts.append("Tags: " + ', '.join(str(tag) for tag in tags if str(tag).strip()))
    if content:
        parts.append("Note content:\n" + content)

    return '\n\n'.join(part for part in parts if part.strip())


def _get_note_context(app, note_id):
    note_obj_id = parse_object_id(note_id, 'note_id')
    if note_obj_id is None:
        return {'success': False, 'message': 'Invalid note ID', 'status': 400}

    user_id = get_jwt_identity()
    note = app.mongo.db.notes.find_one({'_id': note_obj_id, 'user_id': user_id})
    if not note:
        note = app.mongo.db.notes.find_one({'_id': note_obj_id, 'shared_with': user_id})
    if not note:
        return {'success': False, 'message': 'Note not found', 'status': 404}

    note_text = _build_note_context(note)
    normalized = _normalize_context_text(note_text)
    if not normalized:
        return {'success': False, 'message': 'Selected note has no readable content', 'status': 400}

    return {'success': True, 'data': {'text': normalized}}


def _combine_context_parts(parts):
    cleaned = [part for part in (_normalize_context_text(part) for part in parts) if part]
    return '\n\n'.join(cleaned)


def _build_summary_prompt(text):
    return (
        'Summarize the following text in 3-4 bullet points, keeping the summary clear and concise.\n\n' +
        text
    )


def _get_dashboard_numeric_context(app):
    """Return numeric stats used to answer dashboard-specific questions."""
    user_id = get_jwt_identity()

    notes_count = app.mongo.db.notes.count_documents({'user_id': user_id})
    tasks_total = app.mongo.db.tasks.count_documents({'user_id': user_id})
    completed_tasks = app.mongo.db.tasks.count_documents({'user_id': user_id, 'status': 'completed'})
    pending_tasks = tasks_total - completed_tasks

    return (
        "Dashboard numeric context (user-specific):\n"
        f"- Notes: {notes_count}\n"
        f"- Total tasks: {tasks_total}\n"
        f"- Completed tasks: {completed_tasks}\n"
        f"- Pending tasks: {pending_tasks}"
    )


@jwt_required()
def answer_question(app):
    data = request.get_json() or {}
    question = (data.get('message') or data.get('question') or '').strip()
    file_id = data.get('file_id')
    note_id = data.get('note_id')
    direct_context = _normalize_context_text(
        data.get('content') or data.get('study_material') or data.get('extracted_text')
    )

    if not question:
        return resp(False, 'Question is required', status=400)

    context_parts = []

    # Always inject numeric dashboard context so the model can answer questions like "how many tasks".
    context_parts.append(_get_dashboard_numeric_context(app))

    if direct_context:
        context_parts.append(direct_context)

    if note_id:
        note_result = _get_note_context(app, note_id)
        if not note_result.get('success'):
            return resp(
                False,
                note_result.get('message', 'Note context failed'),
                status=note_result.get('status', 400)
            )
        context_parts.append(note_result['data']['text'])

    if file_id:
        file_result = extract_text_from_file(app, file_id)
        if not file_result.get('success'):
            return resp(
                False,
                file_result.get('message', 'File extraction failed'),
                status=file_result.get('status', 400)
            )
        context_parts.append(file_result['data']['text'])

    context_text = _combine_context_parts(context_parts)

    client = get_ai_client()
    if client is None:
        return resp(False, 'AI service is not configured', status=503)

    try:
        response = client.chat.completions.create(
            model=get_ai_model(),
            messages=_build_contextual_messages(question, context_text),
            max_tokens=400,
            temperature=0.4
        )
        ans = response.choices[0].message.content.strip()
        return resp(True, 'Answer generated', {'answer': ans})
    except Exception as e:
        return resp(False, f'AI service error: {str(e)}', status=500)


@jwt_required()
def summarize_text(app):
    data = request.get_json() or {}
    text = data.get('text', '').strip()
    file_id = data.get('file_id')
    note_id = data.get('note_id')

    if note_id:
        note_result = _get_note_context(app, note_id)
        if not note_result.get('success'):
            return resp(
                False,
                note_result.get('message', 'Note context failed'),
                status=note_result.get('status', 400)
            )
        text = note_result['data']['text']

    if file_id:
        file_result = extract_text_from_file(app, file_id)
        if not file_result.get('success'):
            return resp(False, file_result.get('message', 'File extraction failed'), status=file_result.get('status', 400))
        text = file_result['data']['text']

    if not text:
        return resp(False, 'Text, file_id, or note_id is required', status=400)

    client = get_ai_client()
    if client is None:
        return resp(False, 'AI service is not configured', status=503)

    try:
        prompt = _build_summary_prompt(text)
        response = client.chat.completions.create(
            model=get_ai_model(),
            messages=[
                {'role': 'system', 'content': 'You are a helpful assistant. Summarize the given text in 3-4 bullet points.'},
                {'role': 'user', 'content': prompt}
            ],
            max_tokens=300,
            temperature=0.7
        )
        summary = response.choices[0].message.content.strip()
        return resp(True, 'Summary generated', {'summary': summary})
    except Exception as e:
        return resp(False, f'AI service error: {str(e)}', status=500)


@jwt_required()
def generate_quiz(app):
    data = request.get_json() or {}
    topic = data.get('topic', '').strip()
    if not topic:
        return resp(False, 'Topic is required', status=400)

    client = get_ai_client()
    if client is None:
        return resp(False, 'AI service is not configured', status=503)

    try:
        response = client.chat.completions.create(
            model=get_ai_model(),
            messages=[
                {'role': 'system', 'content': 'You are an educational assistant. Create a 5-question academic quiz with answers for the given topic.'},
                {'role': 'user', 'content': f'Create a quiz on: {topic}'}
            ],
            max_tokens=500,
            temperature=0.6
        )
        quiz = response.choices[0].message.content.strip()
        return resp(True, 'Quiz generated', {'quiz': quiz})
    except Exception as e:
        return resp(False, f'AI service error: {str(e)}', status=500)

