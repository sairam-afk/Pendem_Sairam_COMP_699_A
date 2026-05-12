from extensions import db

class Participant(db.Model):
    __tablename__ = "participants"

    id = db.Column(db.Integer, primary_key=True)

    # LINK TO USER
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # NEW: GROUP LINK (IMPORTANT)
    group_id = db.Column(db.Integer, db.ForeignKey("fitness_groups.id"), nullable=True)

    # FITNESS DATA
    fitness_level = db.Column(db.String(20), default="low")
    total_points = db.Column(db.Integer, default=0)

    # TIMESTAMP
    joined_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())

    # RELATIONSHIPS
    activities = db.relationship("Activity", backref="participant", lazy=True)

    def __repr__(self):
        return f"<Participant user_id={self.user_id}, group_id={self.group_id}>"