from .. import index
from flask import abort, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from ...decorators import permission_required
from ...models import Permissions
from ...services import UserService, RecipeService
from ..forms import EditProfileAdminForm, EditProfileForm
from .utils import set_form_attrs, set_obj_attrs


@index.route("/")
def home():
    page = request.args.get("page", 1, type=int)
    pagination, recipes = RecipeService.get_recipes(page)
    return render_template("home.html", pagination=pagination, recipes=recipes)


@index.route("/user/<username>")
def user(username):
    user = UserService.get(username=username)
    if not user:
        abort(404)
    page = request.args.get("page", 1, type=int)
    service = UserService(user)
    pagination, recipes = service.get_user_recipes(page)
    return render_template(
        "user.html", user=user, pagination=pagination, recipes=recipes
    )


@index.route("/user/edit", methods=["GET", "POST"])
@login_required
def edit_user():
    form = EditProfileForm()
    user = current_user._get_current_object()
    if form.validate_on_submit():
        user = set_form_attrs(form, user)
        UserService(user).update(user)
        return redirect(url_for(".user", username=user.username))
    form = set_obj_attrs(user, form)
    return render_template("edit-profile.html", form=form)


@index.route("/user/edit/<int:id>", methods=["GET", "POST"])
@permission_required(Permissions.ADMIN)
def edit_user_admin(id):
    user = UserService.get(id=id)
    if not user:
        abort(404)
    form = EditProfileAdminForm()
    if form.validate_on_submit():
        user = set_form_attrs(form, user, remove_attrs=["confirmed"])
        if form.confirmed.data == True:
            user.confirm_day = -1
        else:
            user.confirm_day = 7
        UserService(user).update(user)
        return redirect(url_for(".user", username=user.username))
    form = set_obj_attrs(user, form, remove_attrs=["confirmed"])
    form.confirmed.data = user.confirm_day == -1
    return render_template("edit-profile.html", form=form)


@index.route("/user/saved/recipes")
@login_required
def saved_recipes():
    user = current_user._get_current_object()
    service = UserService(user)
    page = request.args.get("page", 1, type=int)
    pagination, recipes = service.get_saved_recipes(page)
    return render_template("recipes.html", pagination=pagination, recipes=recipes)


@index.route("/user/saved/menus")
@login_required
def saved_menus():
    user = current_user._get_current_object()
    service = UserService(user)
    page = request.args.get("page", 1, type=int)
    _, saved_menus = service.get_saved_menus(page)
    _, created_meus = service.get_menus(page)
    saved_menus.extend(created_meus)
    return render_template("menus.html", menus=saved_menus)
