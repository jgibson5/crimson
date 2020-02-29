import os
from secret_store import secret_store

basedir = os.path.abspath(os.path.dirname(__file__))

class Config():
    PORT = os.environ.get('PORT') or 5000
    MODE = os.environ.get('MODE') or 'development'

    SECRET_KEY = secret_store.get_secret("app-secret-key", quiet_failure=(MODE=="development")).get("app-secret-key") or 'you-will-never-guess'

    DB_CREDENTIALS = secret_store.get_secret("crimson-db")
    SQLALCHEMY_DATABASE_URI = f"postgresql://{DB_CREDENTIALS['username']}:{DB_CREDENTIALS['password']}@crimson.cpti2eeejc4n.us-east-1.rds.amazonaws.com/postgres"# or \
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    USER_ENABLE_EMAIL = False

