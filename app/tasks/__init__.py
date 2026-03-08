from app.celery_worker import celery
from app.ai_service import AIService
from app.models import Note

@celery.task(bind=True, max_retries=3)
def generate_summary_task(self, note_id, user_id):
    with celery.flask_app.app_context():
        from app.extensions import db
        note = Note.query.get(note_id)
        if not note or note.user_id != user_id:
            return {'error': '笔记不存在或无权限'}
        ai = AIService()
        summary = ai.generate_summary(note.content)
        return {'note_id': note_id, 'summary': summary}

@celery.task(bind=True)
def ask_question_task(self, note_id, user_id, question):
    with celery.flask_app.app_context():
        note = Note.query.get(note_id)
        if not note or note.user_id != user_id:
            return {'error': '笔记不存在或无权限'}
        ai = AIService()
        messages = [
            {"role": "system", "content": f"基于以下笔记内容回答问题：\n{note.content[:3000]}"},
            {"role": "user", "content": question}
        ]
        answer = ai.chat_completion(messages)
        return {'note_id': note_id, 'question': question, 'answer': answer}

@celery.task(bind=True)
def recommend_tags_task(self, content):
    with celery.flask_app.app_context():
        ai = AIService()
        tags = ai.recommend_tags(content)
        return {'tags': tags}