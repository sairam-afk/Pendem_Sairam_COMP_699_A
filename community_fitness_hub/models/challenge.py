from extensions import db

class Challenge(db.Model):
    __tablename__ = "challenges"

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.String(300))

    group_id = db.Column(db.Integer, db.ForeignKey("fitness_groups.id"))

    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)

    status = db.Column(db.String(20), default="upcoming")

    # RELATIONSHIPS
    activities = db.relationship("Activity", backref="challenge", lazy=True)

    def __repr__(self):
        return f"<Challenge {self.title}>"