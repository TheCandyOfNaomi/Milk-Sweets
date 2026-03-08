from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, jsonify, current_app
from flask_login import login_required, current_user
from app import db
from app.models import Note, Tag
from app.forms import NoteForm
from app.tasks import generate_summary_task, ask_question_task, recommend_tags_task
from app.extensions import csrf

notes_bp = Blueprint('notes', __name__, template_folder='../templates/notes')

@notes_bp.route('/')
@login_required
def list_notes():
    page = request.args.get('page', 1, type=int)
    notes = current_user.notes.order_by(Note.updated_at.desc()).paginate(
        page=page, per_page=10, error_out=False)
    return render_template('notes/index.html', notes=notes)

@notes_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_note():
    form = NoteForm()
    if form.validate_on_submit():
        note = Note(title=form.title.data, content=form.content.data, author=current_user)
        if form.tags.data:
            for name in [t.strip().lower() for t in form.tags.data.split(',') if t.strip()]:
                tag = Tag.query.filter_by(name=name).first()
                if not tag:
                    tag = Tag(name=name)
                note.tags.append(tag)
        db.session.add(note)
        db.session.commit()
        flash('笔记已创建', 'success')
        return redirect(url_for('notes.list_notes'))
    return render_template('notes/create.html', form=form)

@notes_bp.route('/<int:id>')
@login_required
def view_note(id):
    note = Note.query.get_or_404(id)
    if note.author != current_user:
        abort(403)
    return render_template('notes/detail.html', note=note)

@notes_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_note(id):
    note = Note.query.get_or_404(id)
    if note.author != current_user:
        abort(403)
    form = NoteForm(obj=note)
    if request.method == 'GET':
        form.tags.data = ', '.join([t.name for t in note.tags])
    if form.validate_on_submit():
        note.title = form.title.data
        note.content = form.content.data
        new_tags = {t.strip().lower() for t in form.tags.data.split(',') if t.strip()}
        current_tags = {t.name for t in note.tags}
        for tag_name in current_tags - new_tags:
            tag = Tag.query.filter_by(name=tag_name).first()
            if tag:
                note.tags.remove(tag)
        for tag_name in new_tags - current_tags:
            tag = Tag.query.filter_by(name=tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.session.add(tag)
            note.tags.append(tag)
        db.session.commit()
        flash('笔记已更新', 'success')
        return redirect(url_for('notes.list_notes'))
    return render_template('notes/edit.html', form=form, note=note)

@notes_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete_note(id):
    note = Note.query.get_or_404(id)
    if note.author != current_user:
        abort(403)
    db.session.delete(note)
    db.session.commit()
    flash('笔记已删除', 'success')
    return redirect(url_for('notes.list_notes'))


@notes_bp.route('/<int:id>/summarize', methods=['POST'])
@login_required
@csrf.exempt
def summarize_async(id):
    note = Note.query.get_or_404(id)
    if note.author != current_user:
        abort(403)
    task = generate_summary_task.delay(note.id, current_user.id)
    return jsonify({'task_id': task.id})

@notes_bp.route('/<int:id>/ask', methods=['POST'])
@login_required
@csrf.exempt
def ask_async(id):
    note = Note.query.get_or_404(id)
    if note.author != current_user:
        abort(403)
    data = request.get_json()
    question = data.get('question', '')
    if not question:
        return jsonify({'error': '问题不能为空'}), 400
    task = ask_question_task.delay(note.id, current_user.id, question)
    return jsonify({'task_id': task.id})

@notes_bp.route('/recommend-tags', methods=['POST'])
@login_required
@csrf.exempt
def recommend_tags():
    data = request.get_json()
    content = data.get('content', '').strip()
    if not content:
        return jsonify({'error': '内容不能为空'}), 400
    task = recommend_tags_task.delay(content)
    return jsonify({'task_id': task.id})

@notes_bp.route('/task/<task_id>/status', methods=['GET'])
@login_required
def task_status(task_id):
    task = current_app.celery.AsyncResult(task_id)
    response = {'state': task.state}
    if task.state == 'SUCCESS':
        response['result'] = task.result
    elif task.state == 'FAILURE':
        response['error'] = str(task.info)
    return jsonify(response)
