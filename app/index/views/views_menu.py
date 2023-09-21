from .. import index
from flask import abort, redirect, render_template, request, session, url_for, flash
from flask_login import current_user, login_required
from ...services import MenuService, RecipeService
from ...models import Menu, Recipe
import json
from .utils import RecipeListEncoder, session_get_menus, remove_recipe_by_name


@index.route("/menu/save-menu/<int:id>")
@login_required
def user_save_menu(id):
    menu = MenuService.get(id=id)
    if not menu:
        abort(404)
    MenuService(menu).save_menu(current_user._get_current_object())
    return redirect(url_for(".menu"))


@index.route("/menu/unsave-menu/<int:id>")
@login_required
def user_unsave_menu(id):
    menu = MenuService.get(id=id)
    if not menu:
        abort(404)
    MenuService(menu).unsave_menu(current_user._get_current_object())
    return redirect(url_for(".menu"))


@index.route("/menu/<int:menu_id>")
def day_menu(menu_id):
    menu = MenuService.get(id=menu_id)
    if not menu:
        abort(404)
    return render_template("day_menu.html", menu=menu)


@index.route("/menu/create")
def create_menu():
    menus = session_get_menus(session)
    return render_template("create-menu.html", menus=menus, editing=0)


@index.route("/menu/create/add-recipe", methods=["POST"])
@login_required
def session_add_recipe():
    recipe_name, menu_idx = request.form["recipe_name"], int(request.form["menu_idx"])
    menus = session_get_menus(session)
    recipe = RecipeService.get(name=recipe_name)
    menus[menu_idx - 1].append(recipe)
    session["menus"] = json.dumps(menus, cls=RecipeListEncoder)
    return render_template(
        "components/_daymenu_response.html", menus=menus, editing=menu_idx
    )


@index.route("/menu/create/remove-recipe", methods=["POST"])
@login_required
def session_remove_recipe():
    recipe_name, menu_idx = request.form["recipe_name"], int(request.form["menu_idx"])
    menus = session_get_menus(session)
    if menu_idx - 1 < len(menus):
        menus[menu_idx - 1] = remove_recipe_by_name(recipe_name, menus[menu_idx - 1])
        session["menus"] = json.dumps(menus, cls=RecipeListEncoder)
    return render_template(
        "components/_daymenu_response.html", menus=menus, editing=menu_idx
    )


@index.route("/menu/create/add-menu", methods=["POST"])
@login_required
def session_add_menu():
    menus = session_get_menus(session)
    menus.append(list())
    session["menus"] = json.dumps(menus, cls=RecipeListEncoder)
    return render_template("components/_daymenu_response.html", menus=menus)


@index.route("/menu/create/remove-menu", methods=["POST"])
@login_required
def session_remove_menu():
    menu_idx = int(request.form["menu_idx"])
    menus = session_get_menus(session)
    if menu_idx - 1 < len(menus):
        menus.pop(menu_idx - 1)
    session["menus"] = json.dumps(menus, cls=RecipeListEncoder)
    return render_template("components/_daymenu_response.html", menus=menus)


@index.route("/menu/create/save-menu")
@login_required
def save_menu():
    menus = session_get_menus(session)
    if menus:
        new_menu = Menu(current_user, len(menus))
        new_menu.day_menus = MenuService.get_day_menus(menus)
        MenuService.add(new_menu)
        session.pop("menus")
        flash("Menu added")
        return redirect(url_for(".saved_menus"))
    return redirect(url_for(".save_menu"))


@index.route("/menu/edit/<int:id>")
@login_required
def edit_menu(id):
    menu = MenuService.get(id=id)
    menus = list(menu.day_menus)
    day_menus = [list(menu.recipes) for menu in menus]
    session["menus"] = json.dumps(day_menus, cls=RecipeListEncoder)
    return render_template("create-menu.html", menus=day_menus, editing=0, edit_menu=id)


@index.route("/menu/create/update-menu/<int:id>")
@login_required
def update_menu(id):
    menus = session_get_menus(session)
    if menus:
        menu = MenuService.get(id=id)
        menu.day_menus = MenuService.get_day_menus(menus)
        menu.day_count = len(menus)
        MenuService.add(menu)
        session.pop("menus")
        flash("Menu updated")
        return redirect(url_for(".saved_menus"))
    return redirect(url_for(".update_menu", id=id))
