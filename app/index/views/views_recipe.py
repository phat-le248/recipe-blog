from ..forms import (
    AddCommentForm,
    CreateRecipeForm,
    EditRecipeAdminForm,
    EditRecipeForm,
)
from .. import index
from flask import abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from ...decorators import admin_required, permission_required
from ...models import Comment, Permissions, Recipe
from ...services import RecipeService, CommentService
from .utils import set_obj_attrs, set_form_attrs


@index.route("/recipe/<int:id>", methods=["GET", "POST"])
def recipe(id):
    recipe = RecipeService.get(id=id)
    page = request.args.get("page", 1, type=int)
    pagination, comments = RecipeService(recipe).recipe_get_comments(page)
    if not recipe:
        abort(404)
    form = AddCommentForm()
    if form.validate_on_submit():
        new_comment = Comment()
        new_comment = set_form_attrs(form, new_comment)
        new_comment.author_id = current_user.id
        new_comment.recipe_id = recipe.id
        CommentService.add(new_comment)
        return redirect(url_for(".recipe", id=recipe.id))
    return render_template(
        "recipe.html",
        recipe=recipe,
        form=form,
        pagination=pagination,
        comments=comments,
    )


@index.route("/recipe/create", methods=["GET", "POST"])
@login_required
def create_recipe():
    form = CreateRecipeForm()
    if form.validate_on_submit():
        new_recipe = Recipe(name="")
        new_recipe = set_form_attrs(form, new_recipe)
        new_recipe.author = current_user._get_current_object()
        RecipeService.add(new_recipe)
        return redirect(url_for(".home"))
    return render_template("create-recipe.html", form=form)


@index.route("/recipe/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_recipe(id):
    recipe = RecipeService.get(id=id)
    if not recipe:
        abort(404)
    if current_user.id != recipe.author_id:
        abort(403)

    form = EditRecipeForm()
    if form.validate_on_submit():
        recipe = set_form_attrs(form, recipe)
        RecipeService(recipe).update(recipe)
        return redirect(url_for(".recipe", id=recipe.id))

    form = set_obj_attrs(recipe, form)
    return render_template("edit-recipe.html", form=form)


@index.route("/recipe/admin-edit/<int:id>", methods=["GET", "POST"])
@login_required
@admin_required
def edit_recipe_admin(id):
    recipe = RecipeService.get(id=id)
    if not recipe:
        abort(404)
    form = EditRecipeAdminForm()
    if form.validate_on_submit():
        recipe = set_form_attrs(form, recipe)
        RecipeService(recipe).update(recipe)
        return redirect(url_for(".recipe", id=recipe.id))

    form = set_obj_attrs(recipe, form)
    return render_template("edit-recipe.html", form=form)


@index.route("/moderate/recipes")
@permission_required(Permissions.MODERATE)
def moderate_recipes():
    page = request.args.get("page", 1, type=int)
    pagination, recipes = RecipeService.get_recipes(page)
    return render_template(
        "moderate-recipes.html", pagination=pagination, recipes=recipes
    )


@index.route("/moderate/recipes/enable/<int:id>")
@permission_required(Permissions.MODERATE)
def enable_recipe(id):
    recipe = RecipeService.get(id=id)
    service = RecipeService(recipe)
    service.enable_recipe()
    flash("Recipe is enable")
    return redirect(url_for(".moderate_recipes"))


@index.route("/moderate/recipes/disable/<int:id>")
@permission_required(Permissions.MODERATE)
def disable_recipe(id):
    recipe = RecipeService.get(id=id)
    service = RecipeService(recipe)
    service.disable_recipe()
    flash("Recipe is disable")
    return redirect(url_for(".moderate_recipes"))


@index.route("/recipe/save/<int:id>")
@login_required
def user_save_recipe(id):
    recipe = RecipeService.get(id=id)
    service = RecipeService(recipe)
    service.save(current_user._get_current_object())
    flash("Saved recipe")
    return redirect(url_for(".home"))


@index.route("/recipe/unsave/<int:id>")
@login_required
def user_unsave_recipe(id):
    recipe = RecipeService.get(id=id)
    service = RecipeService(recipe)
    service.unsave(current_user._get_current_object())
    flash("Unsaved recipe")
    return redirect(url_for(".home"))


@index.route("/recipe/search", methods=["POST"])
def search_recipe():
    query = request.form["query"]
    search_result = RecipeService.search_recipes(Recipe.name, query)
    return render_template(
        "components/_search_response.html", recipes=search_result, in_search=True
    )
