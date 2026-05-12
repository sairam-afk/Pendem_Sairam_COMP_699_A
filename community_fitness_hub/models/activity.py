from extensions import db
from datetime import datetime

class Activity(db.Model):
    __tablename__ = "activities"

    id = db.Column(db.Integer, primary_key=True)

    participant_id = db.Column(db.Integer, db.ForeignKey("participants.id"), nullable=False)
    challenge_id = db.Column(db.Integer, db.ForeignKey("challenges.id"), nullable=False)

    steps = db.Column(db.Integer, default=0)
    workouts = db.Column(db.Integer, default=0)
    active_minutes = db.Column(db.Integer, default=0)

    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Activity Participant {self.participant_id}>"