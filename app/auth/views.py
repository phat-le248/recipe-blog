from flask import current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from . import auth
from .forms import LoginForm, RegisterForm
from ..models import User
from ..services import UserService
from ..mail import send_mail


@auth.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        username_or_mail = form.username_or_mail.data
        password = form.password.data
        remember = form.remember.data

        user = UserService.verify_credential(username_or_mail, password)
        if not user:
            flash("Wrong login information or password")
        else:
            is_unconfirmed = UserService(user).in_confirm_day() is not None
            next = url_for("index.home")
            if is_unconfirmed:
                if user.is_locked:
                    flash("Your account has been locked")
                else:
                    flash(
                        f"Confirm your account before it is locked ({user.confirm_day} day remains)"
                    )
            if not user.is_locked:
                login_user(user, remember=remember)
                next_arg = request.args.get("next", "")
                if next_arg and next_arg.startswith("/"):
                    next = next_arg
            return redirect(next)

    return render_template("auth/login.html", form=form)


@auth.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user_info = {
            "username": form.username.data,
            "mail": form.mail.data,
            "password": form.password.data,
        }
        new_user = User(**user_info)
        UserService.add(new_user)
        flash("You can now login")
        user = UserService.get(username=user_info["username"])
        token = UserService(user).create_confirm_token(
            expiration=current_app.config["APP_CONFIRM_TOKEN_EXPIRATION"]
        )
        send_mail(
            recipients=[user_info["mail"]],
            subject="Email Confirmation",
            template="mail/confirm",
            user=user.username,
            token=token,
        )
        return redirect(url_for(".login"))
    return render_template("auth/register.html", form=form)


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index.home"))


@auth.route("/confirm/<token>")
@login_required
def confirm(token):
    if current_user.confirm_day > 0:
        service = UserService(current_user._get_current_object())
        token_valid = service.verify_confirm_token(token)
        if token_valid:
            flash("Your account is confirmed")
        else:
            flash("Confirm link is invalid or expired")
    return redirect(url_for("index.home"))


@auth.route("/confirm")
@login_required
def resend_confirmation():
    service = UserService(current_user._get_current_object())
    token = service.create_confirm_token(
        expiration=current_app.config["APP_CONFIRM_TOKEN_EXPIRATION"]
    )
    send_mail(
        recipients=[current_user.mail],
        subject="Email Confirmation",
        template="mail/confirm",
        user=current_user.username,
        token=token,
    )
    flash("New confirmation email has been sent")
    return redirect(url_for("index.home"))
