from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required

from extensions import db
from models.user import User
from models.participant import Participant
from models.admin import Admin

auth_bp = Blueprint("auth", __name__)


# ==============================
# 1. HOME
# ==============================
@auth_bp.route("/")
def home():
    return redirect(url_for("auth.login"))


# ==============================
# 2. REGISTER
# ==============================
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        username = request.form.get("username")
        email = request.form.get("email")
        password_raw = request.form.get("password")
        role = request.form.get("role")

        # VALIDATION
        if not username or not email or not password_raw or not role:
            flash("All fields are required")
            return redirect(url_for("auth.register"))

        # CHECK EXISTING USER
        if User.query.filter_by(email=email).first():
            flash("Email already exists")
            return redirect(url_for("auth.register"))

        # HASH PASSWORD
        password = generate_password_hash(password_raw)

        # CREATE USER
        user = User(
            username=username,
            email=email,
            password=password,
            role=role
        )

        db.session.add(user)
        db.session.commit()

        # ROLE BASED INSERT
        if role == "admin":
            db.session.add(Admin(user_id=user.id))
        else:
            db.session.add(Participant(user_id=user.id))

        db.session.commit()

        flash("Registration successful. Please login.")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


# ==============================
# 3. LOGIN (FIXED VERSION)
# ==============================
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        # VALIDATION
        if not email or not password:
            flash("Please enter email and password")
            return redirect(url_for("auth.login"))

        user = User.query.filter_by(email=email).first()

        # HANDLE USER NOT FOUND
        if not user:
            flash("Invalid email or password")
            return redirect(url_for("auth.login"))

        # CHECK PASSWORD
        if not check_password_hash(user.password, password):
            flash("Invalid email or password")
            return redirect(url_for("auth.login"))

        # LOGIN SUCCESS
        login_user(user)

        if user.role == "admin":
            return redirect(url_for("admin.dashboard"))
        else:
            return redirect(url_for("participant.dashboard"))

    return render_template("login.html")


# ==============================
# 4. LOGOUT
# ==============================
@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully")
    return redirect(url_for("auth.login"))