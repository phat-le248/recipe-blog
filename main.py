import os
import unittest

from flask import current_app
from .app import create_app

config_name = os.environ.get("FLASK_CONFIG") or "default"
app = create_app(config_name)


@app.cli.command("test")
def test():
    dir_name = current_app.config["APP_DIR_NAME"]
    tests = unittest.TestLoader().discover(dir_name)
    unittest.TextTestRunner(verbosity=2).run(tests)


if __name__ == "__main__":
    app.run()
