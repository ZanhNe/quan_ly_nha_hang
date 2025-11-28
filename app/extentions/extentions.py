from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from sqlalchemy.orm import DeclarativeBase
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask_socketio import SocketIO



class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base, session_options={'autoflush': False})
ma = Marshmallow()
migrate = Migrate(db=db, render_as_batch=True)

mail = Mail()

bcrypt = Bcrypt()
socketio = SocketIO(cors_allowed_origins='*')