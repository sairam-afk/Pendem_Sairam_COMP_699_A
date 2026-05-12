from extensions import db

class FitnessGroup(db.Model):
    __tablename__ = "fitness_groups"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.String(300))

    admin_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())

    # RELATIONSHIPS
    challenges = db.relationship("Challenge", backref="group", lazy=True)

    def __repr__(self):
        return f"<Group {self.name}>"