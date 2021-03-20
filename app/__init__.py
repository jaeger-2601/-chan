from flask import Flask


def create_app():

    app = Flask(__name__)
    app.config.from_object('config')
    #app.config.from_pyfile('config.py') #load instance config file

    from . import models, auth, utils
    
    models.init_app(app)
    utils.init_app(app)
    
    app.register_blueprint(auth.auth_bp)

    return app


