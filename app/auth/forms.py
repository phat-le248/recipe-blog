from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from ..models import User


class LoginForm(FlaskForm):
    username_or_mail = StringField(
        "Username (or Mail)", validators=[DataRequired(), Length(1, 64)]
    )
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Keep me logged in")
    submit = SubmitField("Login")


class RegisterForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[
            DataRequired(),
            Length(1, 32, "Enter username between 0-32 characters"),
        ],
    )
    mail = StringField("Email", validators=[DataRequired(), Email(), Length(1, 64)])
    password = PasswordField(
        "Password",
        validators=[DataRequired(), EqualTo("password2", "Passwords must be match")],
    )
    password2 = PasswordField("Confirm password", validators=[DataRequired()])
    submit = SubmitField("Register")

    def validate_username(self, field):
        user = User.query.filter_by(username=field.data).first()
        if user:
            raise ValidationError("Username is already taken")

    def validate_email(self, field):
        user = User.query.filter_by(username=field.data).first()
        if user:
            raise ValidationError("Email is already registered")
