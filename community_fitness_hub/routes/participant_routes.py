from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from extensions import db
from models.fitness_group import FitnessGroup
from models.challenge import Challenge
from models.activity import Activity
from models.participant import Participant
from models.user import User

from ai.ai_engine import AIEngine
from ai.decision_tree import DecisionTreeEngine

participant_bp = Blueprint("participant", __name__, url_prefix="/participant")


# ==============================
# 1. DASHBOARD
# ==============================
@participant_bp.route("/dashboard")
@login_required
def dashboard():
    participant = Participant.query.filter_by(user_id=current_user.id).first()
    user = User.query.get(current_user.id)

    # Run AI clustering
    AIEngine.cluster_participants()

    if not participant:
        return render_template(
            "dashboard.html",
            user=user,
            groups=[],
            challenges=[],
            total_score=0,
            fitness_level="Not Assigned",
            progress=0
        )

    activities = Activity.query.filter_by(participant_id=participant.id).all()

    steps = sum(a.steps for a in activities)
    workouts = sum(a.workouts for a in activities)
    minutes = sum(a.active_minutes for a in activities)

    total_score = (steps * 0.1) + (workouts * 10) + (minutes * 0.5)

    fitness_level = participant.fitness_level or "Not Assigned"

    goal = DecisionTreeEngine.assign_goal(
        fitness_level if fitness_level != "Not Assigned" else "low"
    )

    progress = DecisionTreeEngine.evaluate_progress(
        {"steps": steps, "workouts": workouts, "minutes": minutes},
        goal
    )

    groups = FitnessGroup.query.all()
    challenges = Challenge.query.all()

    return render_template(
        "dashboard.html",
        user=user,
        groups=groups,
        challenges=challenges,
        total_score=round(total_score, 2),
        fitness_level=fitness_level,
        progress=progress
    )


# ==============================
# 2. JOIN GROUP
# ==============================
@participant_bp.route("/join_group/<int:group_id>")
@login_required
def join_group(group_id):

    participant = Participant.query.filter_by(user_id=current_user.id).first()

    if not participant:
        flash("Only participants can join groups")
        return redirect(url_for("participant.dashboard"))

    group = FitnessGroup.query.get(group_id)

    if not group:
        flash("Group not found")
        return redirect(url_for("participant.dashboard"))

    # If already joined same group
    if participant.group_id == group_id:
        flash("You are already in this group")
        return redirect(url_for("participant.dashboard"))

    # Assign group
    participant.group_id = group_id
    db.session.commit()

    flash("Successfully joined group")
    return redirect(url_for("participant.dashboard"))


# ==============================
# 3. SUBMIT ACTIVITY
# ==============================
@participant_bp.route("/submit_activity", methods=["POST"])
@login_required
def submit_activity():
    participant = Participant.query.filter_by(user_id=current_user.id).first()

    if not participant:
        flash("Participant not found")
        return redirect(url_for("participant.dashboard"))

    challenge_id = request.form.get("challenge_id")

    if not challenge_id:
        flash("Challenge ID is required")
        return redirect(url_for("participant.dashboard"))

    try:
        activity = Activity(
            participant_id=participant.id,
            challenge_id=int(challenge_id),
            steps=int(request.form.get("steps", 0)),
            workouts=int(request.form.get("workouts", 0)),
            active_minutes=int(request.form.get("minutes", 0))
        )

        db.session.add(activity)
        db.session.commit()

        flash("Activity submitted successfully")

    except Exception as e:
        flash("Error submitting activity")

    return redirect(url_for("participant.dashboard"))