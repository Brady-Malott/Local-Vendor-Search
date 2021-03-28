import os

from config import Config
from flask import Flask

# create and configure the app
app = Flask(__name__, instance_relative_config=True)
app.config.from_object(Config)

# ensure the instance folder exists
try:
    os.makedirs(app.instance_path)
except OSError:
    pass

from . import search
app.register_blueprint(search.bp)