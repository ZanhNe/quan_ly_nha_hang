
from flask import Flask
from app.config import Config
from flask_sqlalchemy import SQLAlchemy
from app.presentation.web.routes.index import index_bp
from app.presentation.web.routes.auth import auth_bp
from app.api.api import api_bp
from app.extentions.extentions import db, ma, migrate, mail, bcrypt, socketio
from app.utils.helper import is_near
from app.admin import init_admin

def create_app() -> Flask:
    app = (Flask(__name__, \
            template_folder='presentation/web/templates'
            , static_folder='presentation/web/static'
            , static_url_path= '/assets'))
    app.config.from_object(obj=Config)
    app.jinja_env.filters['is_near'] = is_near

    ma.init_app(app=app)
    db.init_app(app=app)
    migrate.init_app(app=app)

    mail.init_app(app=app)
    bcrypt.init_app(app=app)
    socketio.init_app(app=app)

    
    init_admin(app)

    app.register_blueprint(blueprint=index_bp)
    app.register_blueprint(blueprint=auth_bp)
    app.register_blueprint(blueprint=api_bp)

    return app





