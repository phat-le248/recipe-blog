from faker import Faker
from .models import User, Comment, Recipe
from ..app import db
from sqlalchemy.exc import IntegrityError


fake = Faker()


def users(n):
    i = 0
    while i < n:
        username = fake.user_name()
        password = fake.password(length=10)
        mail = fake.email()
        name = fake.name()
        location = fake.city()
        about_me = fake.sentence()
        register_since = fake.past_date()

        user = User(
            username=username,
            password=password,
            mail=mail,
            confirm_day=-1,
            name=name,
            location=location,
            about_me=about_me,
            register_since=register_since,
        )
        db.session.add(user)
        try:
            db.session.commit()
            i += 1
        except IntegrityError:
            db.session.rollback()


def comments(n):
    for _ in range(n):
        max_author = User.query.count()
        max_recipe = Recipe.query.count()
        author_offset = fake.random_int(min=0, max=max_author - 1)
        recipe_offset = fake.random_int(min=0, max=max_recipe - 1)
        body = fake.paragraph()

        author = User.query.offset(author_offset).first()
        recipe = Recipe.query.offset(recipe_offset).first()

        comment = Comment(author=author, recipe=recipe, body=body)

        db.session.add(comment)
        db.session.commit()


def recipes(n):
    i = 0
    while i < n:
        name = fake.name()
        max_author = User.query.count()
        author_offset = fake.random_int(min=0, max=max_author - 1)
        how_to = fake.text()
        ingredients = fake.text()
        image_url = fake.image_url()

        author = User.query.offset(author_offset).first()
        recipe = Recipe(
            name=name, author=author, how_to=how_to, ingredients=ingredients
        )
        recipe.image_url = image_url

        db.session.add(recipe)
        try:
            db.session.commit()
            i += 1
        except IntegrityError:
            db.session.rollback()
