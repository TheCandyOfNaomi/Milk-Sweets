from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_caching import Cache

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()
cache = Cache()

login_manager.login_view = 'auth.login'
login_manager.login_message = '请先登录以访问此页面。'

from app.models import User  # 用户模型在 app.models 中，名为 User

@login_manager.user_loader
def load_user(user_id):
    # 从数据库获取用户。注意：user_id 是字符串，可能需要转换为整数。
    # 如果找不到用户，应返回 None（不要抛出异常）。
    return User.query.get(int(user_id))