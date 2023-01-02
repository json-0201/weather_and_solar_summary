from flask import Flask
import secrets

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = secrets.token_hex()

    # import blueprint object from views.py
    from .views import views

    # reference blueprint
    app.register_blueprint(views)

    return app