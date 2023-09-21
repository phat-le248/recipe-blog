import json
from ...models import Recipe


def get_form_attrs(form, remove_attrs=[]):
    attrs = list(form._fields.keys())
    remove_attrs.extend(["csrf_token", "submit"])
    for attr in remove_attrs:
        if attr in attrs:
            attrs.remove(attr)
    return attrs


def set_form_attrs(form, obj, remove_attrs=[]):
    attrs = get_form_attrs(form, remove_attrs)
    for attr in attrs:
        form_data = getattr(form, attr).data
        print(attr)
        setattr(obj, attr, form_data)
    return obj


def set_obj_attrs(obj, form, remove_attrs=[]):
    attrs = get_form_attrs(form, remove_attrs)
    for attr in attrs:
        data = getattr(obj, attr)
        form_attr = getattr(form, attr)
        setattr(form_attr, "data", data)
    return form


def session_get_menus(session) -> list:
    menus = list()
    if "menus" in session and session["menus"] != "":
        menus_cookie = session.get("menus")
        raw_menus = json.loads(menus_cookie)
        menus = [[Recipe(**recipe_dict) for recipe_dict in menu] for menu in raw_menus]
    return menus


def remove_recipe_by_name(recipe_name, recipe_list):
    for recipe in recipe_list:
        if recipe.name == recipe_name:
            recipe_list.remove(recipe)
            break
    return recipe_list


class RecipeListEncoder(json.JSONEncoder):
    def default(self, recipe):
        if isinstance(recipe, Recipe):
            return {"id": recipe.id, "image_url": recipe.image_url, "name": recipe.name}
