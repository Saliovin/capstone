from flask import Flask
from config import app_config
from model import db
from view.view import harvester_api as harvester_blueprint


def create_app(platform):
    app = Flask(__name__)
    app.config.from_object(app_config[platform])
    db.init_app(app)
    app.register_blueprint(harvester_blueprint, url_prefix='/harvester/')

    return app


app = create_app('development')
