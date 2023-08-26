from flask import render_template
from . import index


@index.app_errorhandler(404)
def not_found(e):
    return render_template("errors/404.html")


@index.app_errorhandler(500)
def internal_error(e):
    return render_template("errors/500.html")
