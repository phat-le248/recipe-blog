from flask_wtf import FlaskForm
from wtforms import BooleanField, SelectField, StringField, SubmitField, TextAreaField
from flask_pagedown.fields import PageDownField
from wtforms.validators import DataRequired, Email, Length, ValidationError
from ..models import Recipe, Role


class CreateRecipeForm(FlaskForm):
    name = StringField("Recipe Name", validators=[DataRequired(), Length(1, 128)])
    ingredients = PageDownField("Ingredients", validators=[DataRequired()])
    how_to = PageDownField("Instruction", validators=[DataRequired()])
    image_url = StringField("Image URL")
    submit = SubmitField("Create")

    def validate_name(self, field):
        recipe = Recipe.query.filter_by(name=field.data).first()
        if recipe:
            raise ValidationError("Name is already exist")


class AddCommentForm(FlaskForm):
    body = TextAreaField("Write your comment")
    submit = SubmitField("Post")


class EditProfileForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(1, 64)])
    location = StringField("Location")
    about_me = TextAreaField("About me")
    submit = SubmitField("Save")


class EditProfileAdminForm(FlaskForm):
    mail = StringField("Mail", validators=[DataRequired(), Email(), Length(1, 64)])
    username = StringField("Username", validators=[DataRequired(), Length(1, 32)])
    confirmed = BooleanField("Confirmed")
    role_id = SelectField("Role", coerce=int)
    name = StringField("Name")
    location = StringField("Location")
    about_me = TextAreaField("About me")
    is_locked = BooleanField("Locked")
    submit = SubmitField("Save")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        roles = Role.query.all()
        self.role_id.choices = [(role.id, role.name) for role in roles]


class EditRecipeForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(1, 128)])
    how_to = PageDownField("Instruction", validators=[DataRequired()])
    ingredients = PageDownField("Ingredients", validators=[DataRequired()])
    image_url = StringField("Image URL")
    submit = SubmitField("Save")


class EditRecipeAdminForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(1, 128)])
    how_to = PageDownField("Instruction", validators=[DataRequired()])
    ingredients = PageDownField("Ingredients", validators=[DataRequired()])
    image_url = StringField("Image URL")
    disable = BooleanField("Disable")
    submit = SubmitField("Save")
