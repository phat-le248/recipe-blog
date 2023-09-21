from flask_sqlalchemy.model import Model
from flask import current_app
from .models import (
    DayMenu,
    User,
    Recipe,
    Menu,
    Comment,
    Follow,
    Permissions,
    SaveRecipe,
    SaveMenu,
    Role,
    Modifying,
)
from . import db
from werkzeug.security import check_password_hash
from datetime import datetime, timedelta
import jwt
import hashlib
from markdown import markdown
from bleach import clean, linkify


class Service:
    model = Model

    def __init__(self, model_obj):
        if model_obj is None:
            raise Exception("Service: model_obj can not be None")
        self.model_obj = model_obj

    @classmethod
    def get(cls, **filters):
        result = cls.model.query.filter_by(**filters).first()
        return result

    @staticmethod
    def add(obj):
        db.session.add(obj)
        db.session.commit()

    def update(self, new_obj):
        self.model_obj = new_obj
        db.session.add(self.model_obj)
        db.session.commit()


class UserService(Service):
    model = User

    def verify_password(self, password):
        return check_password_hash(self.model_obj.password_hash, password)

    def can(self, permission):
        return self.model_obj.role.has_permission(permission)

    def is_admin(self):
        return self.model_obj.role.has_permission(Permissions.ADMIN)

    def follow(self, followed):
        if not self.model_obj.is_following(followed):
            f = Follow(follower=self.model_obj, followed=followed)
            db.session.add(f)
            db.session.commit()

    def unfollow(self, followed):
        f = Follow.query.filter_by(
            follower_id=self.model_obj.id, followed_id=followed.id
        ).first()
        if f:
            db.session.delete(f)
            db.session.commit()

    def is_following(self, followed):
        if followed.id is None:
            return False
        f = Follow.query.filter_by(
            follower_id=self.model_obj.id, followed_id=followed.id
        ).first()
        return f is not None

    def is_followed_by(self, follower):
        if follower.id is None:
            return False
        f = Follow.query.filter_by(
            follower_id=follower.id, followed_id=self.model_obj.id
        ).first()
        return f is not None

    def in_confirm_day(self):
        if self.model_obj.confirm_day > 0:
            allowed_days = timedelta(days=7)
            current_day = datetime.now()
            remain_days = (
                (self.model_obj.register_since + allowed_days) - current_day
            ).days
            if remain_days <= 0:
                self.model_obj.is_locked = True
                return False
            self.model_obj.confirm_day = remain_days
            self.update(self.model_obj)
            return True

    def create_confirm_token(self, expiration):
        secret_key = current_app.config["SECRET_KEY"]
        algorithm = current_app.config["JWT_ALGORITHM"]
        payload = {
            "confirm": self.model_obj.id,
            "exp": datetime.utcnow() + timedelta(seconds=expiration),
        }
        token = jwt.encode(payload, secret_key, algorithm)
        return token

    def verify_confirm_token(self, token):
        secret_key = current_app.config["SECRET_KEY"]
        algorithm = current_app.config["JWT_ALGORITHM"]
        try:
            payload = jwt.decode(token, secret_key, algorithm)
        except jwt.exceptions.InvalidTokenError:
            return False
        if self.model_obj.id != payload["confirm"]:
            return False
        self.model_obj.confirm_day = -1
        self.update(self.model_obj)
        return True

    def hashing_mail(self):
        return hashlib.md5(self.model_obj.mail.encode()).hexdigest()

    def gravatar(self, size):
        if not self.model_obj.mail_hashing:
            self.model_obj.mail_hashing = self.model_obj.hashing_mail()
        url = "https://www.gravatar.com/avatar"
        return f"{url}/{self.model_obj.mail_hashing}?s={size}&d=identicon&r=g"

    @staticmethod
    def verify_credential(username_or_mail, password):
        user_by_username = UserService.get(username=username_or_mail)
        user_by_mail = UserService.get(mail=username_or_mail)
        user = user_by_username or user_by_mail
        if user:
            service = UserService(user)
            if service.verify_password(password):
                return user
            return None
        return None

    def get_user_recipes(self, page):
        paginate = self.model_obj.recipes.order_by(
            Recipe.posted_timestamp.desc()
        ).paginate(
            per_page=current_app.config["APP_RECIPES_PER_PAGE"],
            page=page,
            error_out=False,
        )
        user_recipes = paginate.items
        return paginate, user_recipes

    def get_saved_recipes(self, page):
        recipes_query = self.model_obj.saved_recipes.order_by(
            SaveRecipe.timestamp.desc()
        )
        paginate = recipes_query.paginate(
            page=page,
            per_page=current_app.config["APP_RECIPES_PER_PAGE"],
            error_out=False,
        )
        saved_recipes = [item.recipe for item in paginate.items]
        return paginate, saved_recipes

    def get_saved_menus(self, page):
        menus_query = self.model_obj.saved_menus.order_by(SaveMenu.timestamp.desc())
        paginate = menus_query.paginate(
            page=page,
            per_page=current_app.config["APP_MENUS_PER_PAGE"],
            error_out=False,
        )
        saved_menus = [
            {"menu": item.menu, "timestamp": item.timestamp} for item in paginate.items
        ]
        return paginate, saved_menus

    def get_menus(self, page):
        menus_query = self.model_obj.menus.order_by(Menu.timestamp.desc())
        paginate = menus_query.paginate(
            page=page,
            per_page=current_app.config["APP_MENUS_PER_PAGE"],
            error_out=False,
        )
        menus = [{"menu": item, "timestamp": item.timestamp} for item in paginate.items]
        return paginate, menus

    def get_following(self, page):
        following_query = self.model_obj.followers.order_by(Follow.timestamp.desc())
        paginate = following_query.paginate(
            page=page,
            per_page=current_app.config["APP_FOLLOWS_PER_PAGE"],
            error_out=False,
        )
        following = [
            {"user": item.follower, "timestamp": item.timestamp}
            for item in paginate.items
        ]
        return paginate, following

    def get_followed(self, page):
        followed_query = self.model_obj.followed.order_by(Follow.timestamp.desc())
        paginate = followed_query.paginate(
            page=page,
            per_page=current_app.config["APP_FOLLOWS_PER_PAGE"],
            error_out=False,
        )
        followed = [
            {"user": item.followed, "timestamp": item.timestamp}
            for item in paginate.items
        ]
        return paginate, followed


class RecipeService(Service):
    model = Recipe

    def modify(self, modifier):
        modifying = Modifying(self.model_obj, modifier)
        db.session.add(modifying)
        db.session.commit()

    def is_saved(self, user_id):
        saving = SaveRecipe.query.filter_by(
            user_id=user_id, recipe_id=self.model_obj.id
        ).first()
        return saving is not None

    def save(self, user):
        if not self.is_saved(user.id):
            saving = SaveRecipe(user, self.model_obj)
            db.session.add(saving)
            db.session.commit()

    def unsave(self, user):
        if self.is_saved(user.id):
            saving = SaveRecipe.query.filter_by(
                user_id=user.id, recipe_id=self.model_obj.id
            ).first()
            db.session.delete(saving)
            db.session.commit()

    @staticmethod
    def on_update_ingredients(target, value, oldvalue, initiator):
        allowed_tags = ["li", "ul", "ol"]
        markdown_text = markdown(value, output_format="html")
        markdown_processed = linkify(
            clean(markdown_text, tags=allowed_tags, strip=True)
        )
        target.ingredients_html = markdown_processed

    @staticmethod
    def on_update_howto(target, value, oldvalue, initiator):
        allowed_tags = ["li", "ul", "ol"]
        markdown_text = markdown(value, output_format="html")
        markdown_processed = linkify(
            clean(markdown_text, tags=allowed_tags, strip=True)
        )
        target.how_to_html = markdown_processed

    def recipe_get_comments(self, page):
        paginate = self.model_obj.comments.order_by(Comment.timestamp.desc()).paginate(
            page=page,
            per_page=current_app.config["APP_COMMENTS_PER_PAGE"],
            error_out=False,
        )
        comments = paginate.items
        return paginate, comments

    @staticmethod
    def get_recipes(page):
        paginate = Recipe.query.order_by(Recipe.posted_timestamp.desc()).paginate(
            per_page=current_app.config["APP_RECIPES_PER_PAGE"],
            page=page,
            error_out=False,
        )
        recipes = paginate.items
        return paginate, recipes

    def disable_recipe(self):
        if not self.model_obj.disable:
            self.model_obj.disable = True
            self.update(self.model_obj)

    def enable_recipe(self):
        if self.model_obj.disable:
            self.model_obj.disable = False
            self.update(self.model_obj)

    @staticmethod
    def search_recipes(attr, query):
        search_str = f"%{query}%"
        results = (
            Recipe.query.filter(attr.like(search_str))
            .limit(current_app.config["APP_MAX_RECIPE_SEARCH_RESULT"])
            .all()
        )
        return results


class CommentService(Service):
    model = Comment

    @staticmethod
    def get_comments(page):
        paginate = Comment.query.order_by(Comment.timestamp.desc()).paginate(
            per_page=current_app.config["APP_COMMENTS_PER_PAGE"],
            page=page,
            error_out=False,
        )
        comments = paginate.items
        return paginate, comments

    def disable_comment(self):
        if not self.model_obj.disable:
            self.model_obj.disable = True
            self.update(self.model_obj)

    def enable_comment(self):
        if self.model_obj.disable:
            self.model_obj.disable = False
            self.update(self.model_obj)


class MenuService(Service):
    model = Menu

    def save_menu(self, user):
        self.model_obj.save(user)

    def unsave_menu(self, user):
        self.model_obj.unsave(user)

    @staticmethod
    def get_day_menus(menus_list):
        day_menus = list()
        if menus_list:
            for i, recipes in enumerate(menus_list):
                recipes = [RecipeService.get(id=recipe.id) for recipe in recipes]
                day_menu = DayMenu(for_day=i + 1, recipes=recipes)
                day_menus.append(day_menu)
        return day_menus


class RoleService(Service):
    model = Role


class FollowService(Service):
    model = Follow
