import os
import dotenv

root_dir = os.path.abspath(os.path.dirname(__file__))
if os.name == 'posix':
    dotenv.load_dotenv(override=True)
elif os.name == 'nt':
    dotenv.load_dotenv('winRun.env', override=True)

class Config():
    DEBUG = False
    UNIT_TEST = False
    INTEGRATION_TEST = False
    DEV = False
    SECRET_KEY = os.environ['SECRET_KEY']
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']

class DevelopmentConfig(Config):
    DEBUG = True
    UNIT_TEST = True
    DEV = True

class StaggingConfig(Config):
    DEBUG = True
    INTEGRATION_TEST = True

class ProductionConfig(Config):
    pass