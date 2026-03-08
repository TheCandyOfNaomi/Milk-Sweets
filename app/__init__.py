from flask import Flask
from config import Config
from app.extensions import db, migrate, login_manager, csrf, cache

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    cache.init_app(app)

    from app.celery_worker import celery
    app.celery = celery
    celery.flask_app = app
    
    from app.blueprints.auth import auth_bp
    from app.blueprints.main import main_bp
    from app.blueprints.notes import notes_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)
    app.register_blueprint(notes_bp, url_prefix='/notes')

    return app