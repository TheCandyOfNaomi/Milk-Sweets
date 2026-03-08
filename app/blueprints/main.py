from flask import Blueprint, render_template
from flask_login import login_required, current_user
from sqlalchemy import func, extract
from datetime import datetime, timedelta
from app.extensions import cache, db
from app.models import Note, Tag, note_tag

main_bp = Blueprint('main', __name__, template_folder='../templates/main')

@main_bp.route('/')
@login_required
def index():
    recent_notes = current_user.notes.order_by(Note.updated_at.desc()).limit(5).all()
    popular_tags = db.session.query(
        Tag.name, func.count(note_tag.c.note_id).label('usage_count')
    ).join(note_tag, Tag.id == note_tag.c.tag_id)\
     .join(Note, Note.id == note_tag.c.note_id)\
     .filter(Note.user_id == current_user.id)\
     .group_by(Tag.id)\
     .order_by(func.count(note_tag.c.note_id).desc())\
     .limit(5).all()
    return render_template('index.html', recent_notes=recent_notes, popular_tags=popular_tags)

@main_bp.route('/stats')
@login_required
@cache.cached(timeout=300, key_prefix=lambda: f'user_stats_{current_user.id}')
def user_stats():
    note_count = current_user.notes.count()
    tag_count = db.session.query(Tag).join(note_tag, Tag.id == note_tag.c.tag_id)\
                         .join(Note, Note.id == note_tag.c.note_id)\
                         .filter(Note.user_id == current_user.id)\
                         .distinct().count()

    total_words = db.session.query(
        func.sum(func.length(Note.content))
    ).filter(Note.user_id == current_user.id).scalar() or 0

    week_ago = datetime.utcnow() - timedelta(days=7)
    notes_this_week = current_user.notes.filter(Note.created_at >= week_ago).count()

    monthly = db.session.query(
        extract('year', Note.created_at).label('year'),
        extract('month', Note.created_at).label('month'),
        func.count().label('count')
    ).filter(Note.user_id == current_user.id)\
     .group_by('year', 'month')\
     .order_by('year', 'month')\
     .all()
    months = [f"{int(r.year)}-{int(r.month):02d}" for r in monthly]
    counts = [r.count for r in monthly]

    tag_freq = db.session.query(
        Tag.name, func.count(note_tag.c.note_id).label('freq')
    ).join(note_tag, Tag.id == note_tag.c.tag_id)\
     .join(Note, Note.id == note_tag.c.note_id)\
     .filter(Note.user_id == current_user.id)\
     .group_by(Tag.id)\
     .order_by(func.count(note_tag.c.note_id).desc())\
     .limit(10).all()

    longest = current_user.notes.order_by(func.length(Note.content).desc()).first()
    shortest = current_user.notes.order_by(func.length(Note.content).asc()).first()
    avg_len = db.session.query(
        func.avg(func.length(Note.content))
    ).filter(Note.user_id == current_user.id).scalar() or 0

    last_7 = []
    for i in range(6, -1, -1):
        day = (datetime.utcnow() - timedelta(days=i)).date()
        count = current_user.notes.filter(
            func.date(Note.updated_at) == day
        ).count()
        last_7.append({'date': day.strftime('%Y-%m-%d'), 'count': count})

    return render_template('stats.html',
                           note_count=note_count,
                           tag_count=tag_count,
                           total_words=total_words,
                           notes_this_week=notes_this_week,
                           months=months,
                           counts=counts,
                           tag_freq=tag_freq,
                           longest_note=longest,
                           shortest_note=shortest,
                           avg_length=round(avg_len, 2),
                           last_7_days=last_7)

@main_bp.route('/about')
def about():
    return render_template('about.html')