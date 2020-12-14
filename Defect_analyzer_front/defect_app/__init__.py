from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from Defect_analyzer_front.defect_app.config import Config

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'
mail = Mail()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    # extentions
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    from Defect_analyzer_front.defect_app.users.routes import users
    # from Defect_analyzer_front.defect_app.posts_default.routes import posts_default
    from Defect_analyzer_front.defect_app.coilposts.routes import coilposts_blueprint
    from Defect_analyzer_front.defect_app.main.routes import main
    from Defect_analyzer_front.defect_app.errors.handlers import errors
    from Defect_analyzer_front.defect_app.backendconfig.routes import backend_config_blueprint
    from Defect_analyzer_front.defect_app.captcha.routes import captcha_blueprint

    app.register_blueprint(users)
    # app.register_blueprint(posts_default)
    app.register_blueprint(coilposts_blueprint)
    app.register_blueprint(main)
    app.register_blueprint(errors)
    app.register_blueprint(backend_config_blueprint)
    app.register_blueprint(captcha_blueprint)

    return app
