class Config:
    APP_DIR_NAME = "recipe_blog"


class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = "mysql://root:letmein@localhost/recipeblog_dev"


class TestingConfig(Config):
    SQLALCHEMY_DATABASE_URI = "mysql://root:letmein@localhost/recipeblog_test"


config = {
    "development": DevelopmentConfig(),
    "testing": TestingConfig(),
    "default": DevelopmentConfig(),
}
