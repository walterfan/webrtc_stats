import logging
import os
import sys
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_pagedown import PageDown
from flask_sqlalchemy import SQLAlchemy
from .config import config

bootstrap = Bootstrap()
moment = Moment()
db = SQLAlchemy()
pagedown = PageDown()

def create_logger(filename, log2console=True, logLevel=logging.INFO, logFolder='./logs'):
    # add log
    logger = logging.getLogger(filename)
    logger.setLevel(logging.INFO)
    formats = '%(asctime)s - [%(filename)s:%(lineno)d] - %(levelname)s - %(message)s'
    formatter = logging.Formatter(formats)

    logfile = os.path.join(logFolder, filename + '.log')
    directory = os.path.dirname(logfile)
    if not os.path.exists(directory):
        os.makedirs(directory)

    handler = logging.FileHandler(logfile)
    handler.setLevel(logLevel)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    if log2console:
        handler2 = logging.StreamHandler(sys.stdout)
        handler2.setFormatter(logging.Formatter(formats))
        handler2.setLevel(logLevel)
        logger.addHandler(handler2)

    return logger



def create_app(app_name, env_name="default"):
    app = Flask(app_name)
    app.config.from_object(config[env_name])
    #app.config["SECRET_KEY"] = "secret"
    config[env_name].init_app(app)

    config_name = os.getenv('FLASK_CONFIG') or 'default'

    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    pagedown.init_app(app)

    return app

app = create_app("webrtc_stats")
logger = create_logger("webrtc_stats")




