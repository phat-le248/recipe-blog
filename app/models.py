from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from . import db


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
            [i.ingredient for i in origin.ingredients.all()],
            origin.how_to,
        )
        db.session.add(modified_recipe)
        db.session.commit()
        self.new_recipe_id = Recipe.query.filter_by(name=modified_name).first().id


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    mail = db.Column(db.String(64), unique=True, nullable=False)
    confirm_day = db.Column(db.Integer, default=7)
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"))
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text)
    recipes = db.relationship("Recipe", backref="author", lazy="dynamic")
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

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def can(self, permission):
        return self.role.has_permission(permission)

    def is_admin(self):
        return self.role.has_permission(Permissions.ADMIN)

    def follow(self, followed):
        if not self.is_following(followed):
            f = Follow(follower=self, followed=followed)
            db.session.add(f)
            db.session.commit()

    def unfollow(self, followed):
        f = Follow.query.filter_by(follower_id=self.id, followed_id=followed.id).first()
        if f:
            db.session.delete(f)
            db.session.commit()

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


class RecipeIngredient(db.Model):
    ingredient_id = db.Column(
        db.Integer, db.ForeignKey("ingredients.id"), primary_key=True
    )
    recipe_id = db.Column(db.Integer, db.ForeignKey("recipes.id"), primary_key=True)
    amount = db.Column(db.String(32))


class Recipe(db.Model):
    __tablename__ = "recipes"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    posted_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    modified_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    ingredients = db.relationship(
        "RecipeIngredient",
        foreign_keys=[RecipeIngredient.recipe_id],
        backref=db.backref("recipe", lazy="joined"),
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    how_to = db.Column(db.Text)
    comments = db.relationship("Comment", backref="commented_recipe", lazy="dynamic")
    modifiers = db.relationship(
        "Modifying",
        foreign_keys=[Modifying.origin_id],
        backref=db.backref("origin", lazy="joined"),
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    def __init__(self, name, author=None, ingredients=[], how_to=""):
        self.name = name
        if author:
            self.author_id = author.id
        for ingredient in ingredients:
            self.add_ingredient(ingredient)
        self.how_to = how_to

    def add_ingredient(self, ingredient):
        i = RecipeIngredient(recipe=self, ingredient=ingredient)
        db.session.add(i)

    def modify(self, modifier):
        modifying = Modifying(self, modifier)
        db.session.add(modifying)
        db.session.commit()


class Ingredient(db.Model):
    __tablename__ = "ingredients"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    image_url = db.Column(db.String(128))
    used_in = db.relationship(
        "RecipeIngredient",
        foreign_keys=[RecipeIngredient.ingredient_id],
        backref=db.backref("ingredient", lazy="joined"),
        lazy="dynamic",
        cascade="all, delete-orphan",
    )


in_menu = db.Table(
    "in_menu",
    db.Column("recipe_id", db.Integer, db.ForeignKey("recipes.id")),
    db.Column("menu_id", db.Integer, db.ForeignKey("day_menus.id")),
)


class Menu(db.Model):
    __tablename__ = "menus"
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    day_count = db.Column(db.Integer)
    day_menus = db.relationship("DayMenu", backref="menu", lazy="dynamic")

    def __init__(self, owner=None, day_count=None):
        if owner:
            self.owner_id = owner.id
        self.day_count = day_count


class DayMenu(db.Model):
    __tablename__ = "day_menus"
    id = db.Column(db.Integer, primary_key=True)
    menu_id = db.Column(db.Integer, db.ForeignKey("menus.id"), unique=True)
    for_day = db.Column(db.Integer, unique=True)
    recipes = db.relationship(
        "Recipe",
        secondary=in_menu,
        backref=db.backref("menus", lazy="dynamic"),
        lazy="dynamic",
    )

    def __init__(self, menu=None, recipes=[]):
        if menu:
            self.menu_id = menu.id
            created_menus_count = DayMenu.query.filter_by(menu_id=menu.id).count()
            self.for_day = min(menu.day_count, created_menus_count + 1)
        for recipe in recipes:
            self.recipes.append(recipe)


class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    recipe_id = db.Column(db.Integer, db.ForeignKey("recipes.id"))
    body = db.Column(db.Text)

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

    def has_permission(self, permission):
        return self.permissions & permission == permission

    def add_permission(self, permission):
        self.permissions += permission

    def remove_permission(self, permission):
        self.permissions -= permission

    def reset_permission(self):
        self.permissions = 0

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
