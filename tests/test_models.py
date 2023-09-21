from unittest import TestCase
from ..app import create_app
from ..app.models import (
    User,
    Recipe,
    Menu,
    Comment,
    # Ingredient,
    DayMenu,
    Role,
    Permissions,
)
from ..app import db

users_info = [
    {"username": "test", "mail": "test@test.com"},
    {"username": "test1", "mail": "test1@test.com"},
]
ingredients_info = [{"name": "fish"}]
recipes_info = [{"name": "fried fish", "how_to": "just put fish on the pan"}]
menus_info = [{"day_count": 1}]
comments_info = [{"body": "This is a nice dish!!"}]


def create_obj(cls, json=dict(), query_fields=dict(), **kwargs):
    obj = cls(**json, **kwargs)
    db.session.add(obj)
    db.session.commit()
    created_obj = None
    if query_fields:
        created_obj = cls.query.filter_by(**query_fields).first()
    elif json:
        created_obj = cls.query.filter_by(**json).first()
    return created_obj


class TestModel(TestCase):
    def setUp(self):
        app = create_app("testing")
        self.app_ctx = app.app_context()
        self.app_ctx.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_ctx.pop()


class TestUser(TestModel):
    def test_create_user(self):
        user = create_obj(User, users_info[0], password="password")
        self.assertTrue(user is not None)

    def test_verify_password(self):
        user = create_obj(User, users_info[0], password="password")
        if user:
            self.assertTrue(user.verify_password("password"))
            self.assertFalse(user.verify_password("wrong_password"))
        else:
            self.fail()

    def test_password_hashing(self):
        user = create_obj(User, users_info[0], password="password")
        user2 = create_obj(User, users_info[1], password="password")
        if user and user2:
            self.assertTrue(user.password_hash != user2.password_hash)
        else:
            self.fail()

    def test_follow(self):
        user = create_obj(User, users_info[0], password="password")
        user2 = create_obj(User, users_info[1], password="password")
        if user and user2:
            user.follow(user2)
            user2.follow(user)
            self.assertTrue(user.followers.all()[0].follower.username == user2.username)
            self.assertTrue(user.followed.all()[0].followed.username == user2.username)
            self.assertTrue(user.is_following(user2) and user2.is_following(user))
            user2.unfollow(user)
            self.assertFalse(user2.is_following(user))
            self.assertTrue(user2.is_followed_by(user))
        else:
            self.fail()


class TestRecipe(TestModel):
    def test_add_recipe(self):
        # fish = create_obj(Ingredient, ingredients_info[0])
        # self.assertTrue(fish is not None)

        author = create_obj(User, users_info[0], password="password")
        recipe = create_obj(
            Recipe,
            recipes_info[0],
            author=author,
            # ingredients=[fish]
        )
        self.assertTrue(recipe is not None)
        self.assertTrue(author.recipes.count() == 1) if author else self.fail()

        # if recipe:
        #     ingredient = recipe.ingredients[0].ingredient
        #     self.assertTrue(ingredient.name == "fish")
        # else:
        #     self.fail()

    def test_add_modifier(self):
        author = create_obj(User, users_info[0], password="password")
        recipe = create_obj(Recipe, recipes_info[0], author=author)
        if author and recipe:
            recipe.modify(author)
            self.assertTrue(
                recipe.modifiers.all()[0].modifier.username == author.username
            )
            self.assertTrue(author.modified_recipes.all()[0].origin.name == recipe.name)
        else:
            self.fail()


class TestMenu(TestModel):
    def test_add_menu(self):
        owner = create_obj(User, users_info[0], password="password")
        if owner:
            menu = create_obj(Menu, menus_info[0], owner=owner)
            self.assertTrue(menu is not None)
            self.assertTrue(owner.menus.count() == 1)

            if menu:
                recipe = create_obj(Recipe, recipes_info[0])
                menu_day1 = create_obj(
                    DayMenu,
                    menu=menu,
                    query_fields={"menu_id": menu.id},
                    recipes=[recipe],
                )
                self.assertTrue(menu_day1 is not None)
                self.assertTrue(menu_day1.for_day == 1) if menu_day1 else self.fail()

                menu.day_menus.append(menu_day1)
                db.session.add(menu)
                db.session.commit()
                complete_menu = Menu.query.filter_by(owner_id=owner.id).first()
                self.assertTrue(complete_menu.day_menus.count() == 1)
                recipes = complete_menu.day_menus.all()[0].recipes.all()
                self.assertTrue(recipes[0].name == "fried fish")
            else:
                self.fail()
        else:
            self.fail()


class TestComment(TestModel):
    def test_add_comment(self):
        user = create_obj(User, users_info[0], password="password")
        recipe = create_obj(Recipe, recipes_info[0])
        comment = create_obj(Comment, comments_info[0], author=user, recipe=recipe)
        self.assertTrue(comment is not None)
        if recipe and user:
            self.assertTrue(user.comments.count() == 1)
            self.assertTrue(recipe.comments.count() == 1)
        else:
            self.fail()


class TestRole(TestModel):
    def test_insert_role(self):
        Role.insert_roles()
        self.assertEqual(Role.query.count(), 3)

    def test_assign_role(self):
        Role.insert_roles()
        default_role = Role.query.filter_by(default=True).first()
        if default_role:
            user = create_obj(
                User, users_info[0], password="password", role_id=default_role.id
            )
            if user:
                self.assertTrue(
                    user.can(Permissions.FOLLOW)
                    and user.can(Permissions.COMMENT)
                    and user.can(Permissions.WRITE)
                )
                self.assertFalse(user.is_admin())
        else:
            self.fail()
