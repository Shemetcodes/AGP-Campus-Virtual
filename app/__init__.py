from flask import Flask
from flask_mongoengine import MongoEngine
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap

from config import DevConfig

class Msg:
    class Flash:
        LOGOUT_USER = "Ha cerrado sesión correctamente."
        NEW_USER = "Bienvenido {first_name}."
        INVALID_CREDENTIALS = "Correo o contraseña inválidos."

    class UserRegistration:
        ERROR_REQUIRED_FIELD = "Este campo es obligatorio."
        ERROR_PASSWORD_MATCH = "Las contraseñas deben coincidir."
        ERROR_EMAIL_IN_USE = "La dirección de correo ya ha sido registrada."
        ERROR_ACCEPT_TERMS = "Debe aceptar los términos y condiciones para continuar."
        ERROR_INVALID_EMAIL = "Por favor introduzca una dirección de correo válida."
        
        ERROR_PASSWORD_LENGTH = "La contraseña debe medir entre 8 y 64 caracteres."
        ERROR_PASSWORD_AT_LEAST_ONE_NUMBER = "La contraseña debe conenter al menos un número."
        ERROR_PASSWORD_AT_LEAST_ONE_UPPERCASE = "La contraseña debe conenter al menos una letra mayúscula."
        ERROR_PASSWORD_AT_LEAST_ONE_LOWERCASE = "La contraseña debe conenter al menos una letra minúscula."
        ERROR_PASSWORD_AT_LEAST_ONE_SPECIAL_CHARACTER = "La contraseña debe contener al menos un caracter especial: {}."
        
        ACCEPT_TERMS = "He leído y acepto los términos y condiciones."


db = MongoEngine()
migrate = Migrate()
login = LoginManager()
bootstrap = Bootstrap()

def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    bootstrap.init_app(app)

    return app

# NOTE: Remember to change configuration for production.
app = create_app(DevConfig)

# Keep this import below the app instantiation
from app import routes, models