from flask import Flask
from extensions import db, login_manager
from config import Config   # ✅ USE CONFIG

def create_app():
    app = Flask(__name__)

    # LOAD CONFIG
    app.config.from_object(Config)

    # INIT EXTENSIONS
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    # IMPORT MODELS
    from models.user import User
    from models.participant import Participant
    from models.admin import Admin
    from models.fitness_group import FitnessGroup
    from models.challenge import Challenge
    from models.activity import Activity

    # USER LOADER
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # REGISTER ROUTES
    from routes.auth_routes import auth_bp
    from routes.admin_routes import admin_bp
    from routes.participant_routes import participant_bp
    from routes.challenge_routes import challenge_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(participant_bp)
    app.register_blueprint(challenge_bp)

    # CREATE DB
    with app.app_context():
        db.create_all()

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)