from extensions import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    role = db.Column(db.String(20), nullable=False)

    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())

    # RELATIONSHIPS
    participant = db.relationship("Participant", backref="user", uselist=False)
    admin = db.relationship("Admin", backref="user", uselist=False)

    def __repr__(self):
        return f"<User {self.username}>"