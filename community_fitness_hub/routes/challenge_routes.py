from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from extensions import db
from models.challenge import Challenge
from models.participant import Participant
from models.user import User
from models.activity import Activity

from ai.ai_engine import AIEngine
from ai.decision_tree import DecisionTreeEngine

challenge_bp = Blueprint("challenge", __name__, url_prefix="/challenge")


# ==============================
# 1. VIEW ALL CHALLENGES
# ==============================
@challenge_bp.route("/list")
@login_required
def list_challenges():
    challenges = Challenge.query.all()
    return render_template("challenge.html", challenges=challenges)


# ==============================
# 2. ENROLL IN CHALLENGE
# ==============================
@challenge_bp.route("/enroll/<int:challenge_id>")
@login_required
def enroll(challenge_id):
    participant = Participant.query.filter_by(user_id=current_user.id).first()

    if not participant:
        flash("You must be a participant to join challenges")
        return redirect(url_for("participant.dashboard"))

    challenge = Challenge.query.get(challenge_id)

    if not challenge:
        flash("Challenge not found")
        return redirect(url_for("challenge.list_challenges"))

    # simple enrollment check (avoid duplicate activity records)
    existing = Activity.query.filter_by(
        participant_id=participant.id,
        challenge_id=challenge_id
    ).first()

    if existing:
        flash("Already enrolled in this challenge")
        return redirect(url_for("challenge.list_challenges"))

    # create empty activity entry to mark enrollment
    activity = Activity(
        participant_id=participant.id,
        challenge_id=challenge_id,
        steps=0,
        workouts=0,
        active_minutes=0
    )

    db.session.add(activity)
    db.session.commit()

    flash("Successfully enrolled in challenge")
    return redirect(url_for("participant.dashboard"))


# ==============================
# 3. AI LEADERBOARD (FINAL)
# ==============================
@challenge_bp.route("/leaderboard")
@login_required
def leaderboard():

    # ensure clustering is updated
    AIEngine.cluster_participants()

    leaderboard_data = AIEngine.generate_leaderboard()

    # OPTIONAL: add performance label
    for item in leaderboard_data:
        progress = 0

        # find participant progress
        participant = Participant.query.join(User).filter(
            User.username == item["username"]
        ).first()

        if participant:
            activities = Activity.query.filter_by(participant_id=participant.id).all()

            total_steps = sum(a.steps for a in activities)
            total_workouts = sum(a.workouts for a in activities)
            total_minutes = sum(a.active_minutes for a in activities)

            goal = DecisionTreeEngine.assign_goal(participant.fitness_level or "low")

            progress = DecisionTreeEngine.evaluate_progress(
                {
                    "steps": total_steps,
                    "workouts": total_workouts,
                    "minutes": total_minutes
                },
                goal
            )

        item["progress"] = progress
        item["performance"] = DecisionTreeEngine.get_performance_level(progress)

    return render_template("leaderboard.html", leaderboard=leaderboard_data)