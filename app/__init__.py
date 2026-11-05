from flask import Flask, render_template
from flask_wtf.csrf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from .config import config


db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()


def create_app(config_name="development"):
    app = Flask(__name__)

    app.config.from_object(
        config.get(config_name, config["default"])
    )

    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    from .views import main_bp
    app.register_blueprint(main_bp)

    from .users import users_bp
    app.register_blueprint(users_bp)

    from .products import products_bp
    app.register_blueprint(products_bp)

    from .posts import post_bp
    app.register_blueprint(post_bp)

    from .posts import models

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template("404.html"), 404

    return app
