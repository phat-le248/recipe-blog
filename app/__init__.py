from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_pagedown import PageDown
from flask_moment import Moment
from ..config import config

db = SQLAlchemy()
bootstrap = Bootstrap()
migrate = Migrate(db=db)
login_manager = LoginManager()
login_manager.login_view = "auth.login"
mail = Mail()
pagedown = PageDown()
moment = Moment()


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)
    bootstrap.init_app(app)
    migrate.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    pagedown.init_app(app)
    moment.init_app(app)

    from . import models
    from .index import index
    from .auth import auth
    from .models import Permissions

    @index.app_context_processor
    def inject_permission():
        return dict(Permissions=Permissions)

    app.register_blueprint(index)
    app.register_blueprint(auth, url_prefix="/auth")

    return app
