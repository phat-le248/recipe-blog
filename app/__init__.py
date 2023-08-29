from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate
from ..config import config

db = SQLAlchemy()
bootstrap = Bootstrap()
migrate = Migrate(db=db)


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)
    bootstrap.init_app(app)
    migrate.init_app(app)
    from . import models

    from .index import index

    app.register_blueprint(index)
    return app
