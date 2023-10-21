import os


class Config:
    APP_DIR_NAME = "recipe_blog"
    SECRET_KEY = os.environ.get("SECRET_KEY") or "thisisasecretkey"
    JWT_ALGORITHM = "HS256"
    APP_CONFIRM_TOKEN_EXPIRATION = 900
    MAIL_SERVER = "smtp.googlemail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = (
        os.environ.get("ADMIN_MAIL") or "RecipeBlog Admin <ltphat248@gmail.com>"
    )
    APP_MAIL_SUBJECT_PREFIX = "[Recipe Blog] "
    APP_RECIPES_PER_PAGE = 10
    APP_MENUS_PER_PAGE = 10
    APP_COMMENTS_PER_PAGE = 10
    APP_FOLLOWS_PER_PAGE = 10
    APP_MAX_RECIPE_SEARCH_RESULT = 10


class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = "mysql://root:password@localhost/recipeblog_dev"


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "mysql://root:password@localhost/recipeblog_test"


config = {
    "development": DevelopmentConfig(),
    "testing": TestingConfig(),
    "default": DevelopmentConfig(),
}
