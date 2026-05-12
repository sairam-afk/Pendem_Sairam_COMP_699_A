from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from extensions import db
from models.fitness_group import FitnessGroup
from models.challenge import Challenge
from models.user import User

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


# ==============================
# 1. ADMIN ACCESS CHECK
# ==============================
def is_admin():
    return current_user.is_authenticated and current_user.role == "admin"


# ==============================
# 2. ADMIN DASHBOARD
# ==============================
@admin_bp.route("/dashboard")
@login_required
def dashboard():
    if not is_admin():
        flash("Access denied: Admin only")
        return redirect(url_for("participant.dashboard"))

    groups = FitnessGroup.query.all()
    users = User.query.all()
    challenges = Challenge.query.all()

    return render_template(
        "dashboard.html",
        user=current_user,   # ✅ FIX (IMPORTANT)
        groups=groups,
        users=users,
        challenges=challenges,
        total_score=0,
        fitness_level="Admin",
        progress=0
    )


# ==============================
# 3. CREATE GROUP
# ==============================
@admin_bp.route("/create_group", methods=["POST"])
@login_required
def create_group():
    if not is_admin():
        flash("Access denied")
        return redirect(url_for("participant.dashboard"))

    name = request.form.get("name")
    description = request.form.get("description")

    if not name or not description:
        flash("All fields are required")
        return redirect(url_for("admin.dashboard"))

    group = FitnessGroup(
        name=name,
        description=description,
        admin_id=current_user.id
    )

    db.session.add(group)
    db.session.commit()

    flash("Group created successfully")
    return redirect(url_for("admin.dashboard"))


# ==============================
# 4. DELETE GROUP
# ==============================
@admin_bp.route("/delete_group/<int:group_id>")
@login_required
def delete_group(group_id):
    if not is_admin():
        flash("Access denied")
        return redirect(url_for("participant.dashboard"))

    group = FitnessGroup.query.get(group_id)

    if not group:
        flash("Group not found")
        return redirect(url_for("admin.dashboard"))

    db.session.delete(group)
    db.session.commit()

    flash("Group deleted successfully")
    return redirect(url_for("admin.dashboard"))


# ==============================
# 5. CREATE CHALLENGE
# ==============================
@admin_bp.route("/create_challenge", methods=["POST"])
@login_required
def create_challenge():
    if not is_admin():
        flash("Access denied")
        return redirect(url_for("participant.dashboard"))

    title = request.form.get("title")
    description = request.form.get("description")
    group_id = request.form.get("group_id")

    if not title or not description or not group_id:
        flash("All fields are required")
        return redirect(url_for("admin.dashboard"))

    group = FitnessGroup.query.get(group_id)

    if not group:
        flash("Invalid group selected")
        return redirect(url_for("admin.dashboard"))

    challenge = Challenge(
        title=title,
        description=description,
        group_id=int(group_id),
        status="active"
    )

    db.session.add(challenge)
    db.session.commit()

    flash("Challenge created successfully")
    return redirect(url_for("admin.dashboard"))