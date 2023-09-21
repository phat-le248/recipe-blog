from datetime import datetime
from flask_login import AnonymousUserMixin, UserMixin
from flask_wtf.csrf import hashlib
from werkzeug.security import generate_password_hash
from . import db
from . import login_manager


class Follow(db.Model):
    __tablename__ = "follows"
    follower_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class Modifying(db.Model):
    origin_id = db.Column(db.Integer, db.ForeignKey("recipes.id"), primary_key=True)
    new_recipe_id = db.Column(db.Integer)  #!!!
    modifier_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, origin, modifier):
        if origin:
            self.origin_id = origin.id
        if modifier:
            self.modifier_id = modifier.id

        modified_name = origin.name + f"[{modifier.username}]"
        modified_recipe = Recipe(
            modified_name,
            modifier,
            origin.how_to,
        )
        db.session.add(modified_recipe)
        db.session.commit()
        self.new_recipe_id = Recipe.query.filter_by(name=modified_name).first().id


class SaveRecipe(db.Model):
    __tablename__ = "save_recipes"
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey("recipes.id"), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, user, recipe):
        if user:
            self.user_id = user.id
        if recipe:
            self.recipe_id = recipe.id


class SaveMenu(db.Model):
    __tablename__ = "save_menus"
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    menu_id = db.Column(db.Integer, db.ForeignKey("menus.id"), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, user, menu):
        if user:
            self.user_id = user.id
        if menu:
            self.recipe_id = menu.id


class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    mail = db.Column(db.String(64), unique=True, nullable=False)
    register_since = db.Column(db.DateTime, default=datetime.utcnow)
    confirm_day = db.Column(db.Integer, default=7)
    is_locked = db.Column(db.Boolean, default=False)
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"))
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text)
    mail_hashing = db.Column(db.String(128))
    recipes = db.relationship("Recipe", backref="author", lazy="dynamic")
    saved_recipes = db.relationship(
        "SaveRecipe",
        foreign_keys=[SaveRecipe.user_id],
        backref=db.backref("saved_user", lazy="joined"),
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    saved_menus = db.relationship(
        "SaveMenu",
        foreign_keys=[SaveMenu.user_id],
        backref=db.backref("saved_user", lazy="joined"),
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    menus = db.relationship("Menu", backref="owner", lazy="dynamic")
    comments = db.relationship("Comment", backref="author", lazy="dynamic")
    followed = db.relationship(
        "Follow",
        foreign_keys=[Follow.follower_id],
        backref=db.backref("follower", lazy="joined"),
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    followers = db.relationship(
        "Follow",
        foreign_keys=[Follow.followed_id],
        backref=db.backref("followed", lazy="joined"),
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    modified_recipes = db.relationship(
        "Modifying",
        foreign_keys=[Modifying.modifier_id],
        backref=db.backref("modifier", lazy="joined"),
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    @property
    def password(self):
        raise AttributeError

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def __init__(self, **kwargs):
        for kwarg in kwargs:
            setattr(self, kwarg, kwargs[kwarg])

        default_role = Role.query.filter_by(default=True).first()
        if self.role_id is None:
            self.role_id = default_role.id

    def can(self, permission):
        return self.role.permissions & permission == permission

    def is_admin(self):
        return self.can(Permissions.ADMIN)

    def hashing_mail(self):
        return hashlib.md5(self.mail.encode()).hexdigest()

    def gravatar(self, size):
        if not self.mail_hashing:
            self.mail_hashing = self.hashing_mail()
        url = "https://www.gravatar.com/avatar"
        return f"{url}/{self.mail_hashing}?s={size}&d=identicon&r=g"

    def is_following(self, followed):
        if followed.id is None:
            return False
        f = Follow.query.filter_by(follower_id=self.id, followed_id=followed.id).first()
        return f is not None

    def is_followed_by(self, follower):
        if follower.id is None:
            return False
        f = Follow.query.filter_by(follower_id=follower.id, followed_id=self.id).first()
        return f is not None


@login_manager.user_loader
def user_loader(id):
    return User.query.get(int(id))


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_admin(self):
        return False


login_manager.anonymous_user = AnonymousUser


class Recipe(db.Model):
    __tablename__ = "recipes"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    posted_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    modified_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    image_url = db.Column(db.Text)
    ingredients = db.Column(db.Text)
    ingredients_html = db.Column(db.Text)
    how_to = db.Column(db.Text)
    how_to_html = db.Column(db.Text)
    disable = db.Column(db.Boolean, default=False)
    comments = db.relationship("Comment", backref="commented_recipe", lazy="dynamic")
    modifiers = db.relationship(
        "Modifying",
        foreign_keys=[Modifying.origin_id],
        backref=db.backref("origin", lazy="joined"),
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    saved_users = db.relationship(
        "SaveRecipe",
        foreign_keys=[SaveRecipe.recipe_id],
        backref=db.backref("recipe", lazy="joined"),
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    def is_saved(self, user_id):
        saving = SaveRecipe.query.filter_by(user_id=user_id, recipe_id=self.id).first()
        return saving is not None


in_menu = db.Table(
    "in_menu",
    db.Column("recipe_id", db.Integer, db.ForeignKey("recipes.id")),
    db.Column("menu_id", db.Integer, db.ForeignKey("day_menus.id")),
)


class Menu(db.Model):
    __tablename__ = "menus"
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    day_count = db.Column(db.Integer)
    day_menus = db.relationship("DayMenu", backref="menu", lazy="dynamic")
    saved_users = db.relationship(
        "SaveMenu",
        foreign_keys=[SaveMenu.menu_id],
        backref=db.backref("menu", lazy="joined"),
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    def __init__(self, owner=None, day_count=None):
        if owner:
            self.owner_id = owner.id
        self.day_count = day_count


class DayMenu(db.Model):
    __tablename__ = "day_menus"
    id = db.Column(db.Integer, primary_key=True)
    menu_id = db.Column(db.Integer, db.ForeignKey("menus.id"))
    for_day = db.Column(db.Integer)
    recipes = db.relationship(
        "Recipe",
        secondary=in_menu,
        backref=db.backref("menus", lazy="dynamic"),
        lazy="dynamic",
    )

    def __init__(self, menu=None, for_day=None, recipes=[]):
        if menu:
            self.menu_id = menu.id
            created_menus_count = DayMenu.query.filter_by(menu_id=menu.id).count()
            self.for_day = min(menu.day_count, created_menus_count + 1)
        if for_day:
            self.for_day = for_day
        for recipe in recipes:
            self.recipes.append(recipe)


class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    recipe_id = db.Column(db.Integer, db.ForeignKey("recipes.id"))
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    disable = db.Column(db.Boolean, default=False)

    def __init__(self, author=None, recipe=None, body=""):
        if author:
            self.author_id = author.id
        if recipe:
            self.recipe_id = recipe.id
        self.body = body


class Role(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False)
    permissions = db.Column(db.Integer, default=0)
    users = db.relationship("User", backref="role", lazy="dynamic")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.permissions == None:
            self.permissions = 0

    def add_permission(self, perm):
        self.permissions += perm

    @staticmethod
    def insert_roles():
        roles = {
            "USER": [Permissions.FOLLOW, Permissions.COMMENT, Permissions.WRITE],
            "MODERATOR": [
                Permissions.FOLLOW,
                Permissions.COMMENT,
                Permissions.WRITE,
                Permissions.MODERATE,
            ],
            "ADMIN": [
                Permissions.FOLLOW,
                Permissions.COMMENT,
                Permissions.WRITE,
                Permissions.MODERATE,
                Permissions.ADMIN,
            ],
        }
        default_role = "USER"
        for role_name in roles:
            role = Role.query.filter_by(name=role_name).first()
            if role == None:
                role = Role(name=role_name)
            for perm in roles[role_name]:
                role.add_permission(perm)
            role.default = role_name == default_role
            db.session.add(role)
        db.session.commit()


class Permissions:
    FOLLOW = 1
    COMMENT = 2
    WRITE = 4
    MODERATE = 8
    ADMIN = 16


from .services import RecipeService

db.event.listen(Recipe.ingredients, "set", RecipeService.on_update_ingredients)
db.event.listen(Recipe.how_to, "set", RecipeService.on_update_howto)
