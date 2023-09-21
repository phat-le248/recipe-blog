import os
import unittest
from flask import current_app
from .app import create_app, db
from .app.models import Role
from .app import fake

config_name = os.environ.get("FLASK_CONFIG") or "default"
app = create_app(config_name)


@app.cli.command("test")
def test():
    dir_name = current_app.config["APP_DIR_NAME"]
    tests = unittest.TestLoader().discover(dir_name)
    unittest.TextTestRunner(verbosity=2).run(tests)


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, role=Role, fake=fake)


if __name__ == "__main__":
    app.run()
