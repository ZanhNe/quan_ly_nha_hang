from flask import Flask
from app.presentation.web.routes.test import test

def create_app() -> Flask:
    app = Flask(__name__, \
            template_folder='presentation/web/templates', \
            static_folder='presentation/web/static', \
            static_url_path= '/assets')
    app.register_blueprint(test)
    return app


