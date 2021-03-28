import os
from dotenv import load_dotenv

load_dotenv()
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    #its a key used as a signature key used to make sure the content sent isnt intercepted
    SECRET_KEY = os.environ.get('SECRET_KEY') or "secret_string"
    ENV = os.getenv('FLASK_ENV', default='production')
    DEBUG = ENV == 'development'
    API_KEY = os.environ.get('API_KEY')