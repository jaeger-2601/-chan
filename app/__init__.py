from flask import Flask

app = Flask(__name__)
app.config.from_object('config')

def init_app():

    from . import models
    models.init_app(app)

init_app()

