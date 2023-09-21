from flask import current_app, render_template
from flask_mail import Message
from . import mail


def send_mail(recipients, subject, template, **kwargs):
    msg = Message(
        subject=current_app.config["APP_MAIL_SUBJECT_PREFIX"] + subject,
        recipients=recipients,
        body=render_template(template + ".txt", **kwargs),
        html=render_template(template + ".html", **kwargs),
    )
    mail.send(msg)
