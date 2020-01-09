import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super-secret-key'
    PC_HOST = os.environ.get('PC_HOST', None)
    PC_PORT = os.environ.get('PC_PORT', None)
    USERNAME = os.environ.get('USERNAME', None)
    PASSWORD = os.environ.get('PASSWORD', None)
    VERIFY_SSL = False
    HTTPS = True
    HTTP_TIMEOUT = 3
    APP_TITLE = 'Oner Prism CLI'
    WELCOME_MSG = '''
    Welcome to this CLI tool to demo Prism Rest API
    '''

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True


class TestConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    VERIFY_SSL = True


config = {
    'development': DevelopmentConfig,
    'testing': TestConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}