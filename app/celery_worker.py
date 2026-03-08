import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from celery import Celery
from config import Config

celery = Celery('pkms')
celery.config_from_object(Config, namespace='CELERY')
celery.autodiscover_tasks(['app'])

def init_flask_app():
    from app import create_app
    flask_app = create_app()
    celery.flask_app = flask_app
    return flask_app

init_flask_app()