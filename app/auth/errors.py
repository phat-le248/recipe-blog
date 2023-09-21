from flask import render_template
from . import auth


@auth.app_errorhandler(403)
def forbidden(e):
    return render_template("errors/403.html"), 403
