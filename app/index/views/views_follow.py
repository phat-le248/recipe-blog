from flask import abort, render_template
from flask_login import current_user, login_required
from flask_login.login_manager import flash, redirect
from flask_login.utils import url_for
from flask_wtf.csrf import request
from .. import index
from ...services import UserService


@index.route("/follow/follow/<int:user_id>")
@login_required
def follow(user_id):
    followed = UserService.get(id=user_id)
    if not followed:
        abort(404)
    user = current_user._get_current_object()
    UserService(user).follow(followed)
    flash(f"You are now following user {followed.username}")
    return redirect(url_for(".user", username=followed.username))


@index.route("/follow/unfollow/<int:user_id>")
@login_required
def unfollow(user_id):
    followed = UserService.get(id=user_id)
    if not followed:
        abort(404)
    user = current_user._get_current_object()
    UserService(user).unfollow(followed)
    flash(f"You are now unfollowing user {followed.username}")
    return redirect(url_for(".user", username=followed.username))


@index.route("/follow/following/<username>")
def following(username):
    # return follow template with list of users that request user is following
    user = UserService.get(username=username)
    if not user:
        abort(404)
    page = request.args.get("page", 1, type=int)
    pagination, following = UserService(user).get_following(page)
    return render_template(
        "follow.html",
        user=user,
        pagination=pagination,
        follows=following,
        title="Followed by",
        endpoint=".following",
    )


@index.route("/follow/followed/<username>")
def followed(username):
    # return follow template with list of users following request user
    user = UserService.get(username=username)
    if not user:
        abort(404)
    page = request.args.get("page", 1, type=int)
    pagination, followed = UserService(user).get_followed(page)
    return render_template(
        "follow.html",
        user=user,
        pagination=pagination,
        follows=followed,
        title="Followers of",
        endpoint=".followed",
    )
