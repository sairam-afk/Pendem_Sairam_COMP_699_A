import numpy as np
from sklearn.cluster import KMeans

from models.participant import Participant
from models.activity import Activity
from models.user import User
from extensions import db

from ai.decision_tree import DecisionTreeEngine


class AIEngine:

    # ==============================
    # 1. COLLECT ACTIVITY DATA
    # ==============================
    @staticmethod
    def collect_activity_data():
        participants = Participant.query.all()
        data = []
        mapping = []

        for p in participants:
            activities = Activity.query.filter_by(participant_id=p.id).all()

            total_steps = sum(a.steps for a in activities)
            total_workouts = sum(a.workouts for a in activities)
            total_minutes = sum(a.active_minutes for a in activities)

            data.append([total_steps, total_workouts, total_minutes])
            mapping.append(p)

        return np.array(data), mapping

    # ==============================
    # 2. NORMALIZATION
    # ==============================
    @staticmethod
    def normalize_data(data):
        if len(data) == 0:
            return data

        max_vals = np.max(data, axis=0)
        max_vals[max_vals == 0] = 1

        return data / max_vals

    # ==============================
    # 3. CLUSTER PARTICIPANTS
    # ==============================
    @staticmethod
    def cluster_participants():
        data, participants = AIEngine.collect_activity_data()

        if len(data) < 3:
            return "Not enough data for clustering"

        normalized = AIEngine.normalize_data(data)

        kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
        labels = kmeans.fit_predict(normalized)

        # Dynamic cluster mapping based on activity level
        cluster_centers = kmeans.cluster_centers_
        intensity = [sum(center) for center in cluster_centers]

        sorted_clusters = sorted(range(len(intensity)), key=lambda i: intensity[i])

        cluster_map = {}
        cluster_map[sorted_clusters[0]] = "low"
        cluster_map[sorted_clusters[1]] = "medium"
        cluster_map[sorted_clusters[2]] = "high"

        for i, p in enumerate(participants):
            p.fitness_level = cluster_map.get(labels[i], "low")

        db.session.commit()

        return "Clustering completed successfully"

    # ==============================
    # 4. BALANCED TEAM FORMATION
    # ==============================
    @staticmethod
    def form_balanced_teams(team_size=3):
        participants = Participant.query.all()

        low = [p for p in participants if p.fitness_level == "low"]
        medium = [p for p in participants if p.fitness_level == "medium"]
        high = [p for p in participants if p.fitness_level == "high"]

        teams = []

        max_len = max(len(low), len(medium), len(high), 1)

        for i in range(max_len):
            team = []

            if i < len(low):
                team.append(low[i])
            if i < len(medium):
                team.append(medium[i])
            if i < len(high):
                team.append(high[i])

            if team:
                teams.append(team)

        return teams

    # ==============================
    # 5. GENERATE GOALS
    # ==============================
    @staticmethod
    def generate_goals():
        participants = Participant.query.all()
        goals = {}

        for p in participants:
            level = p.fitness_level or "low"
            goals[p.id] = DecisionTreeEngine.assign_goal(level)

        return goals

    # ==============================
    # 6. EVALUATE PROGRESS
    # ==============================
    @staticmethod
    def evaluate_all_progress():
        participants = Participant.query.all()
        results = {}

        for p in participants:
            activities = Activity.query.filter_by(participant_id=p.id).all()

            total_steps = sum(a.steps for a in activities)
            total_workouts = sum(a.workouts for a in activities)
            total_minutes = sum(a.active_minutes for a in activities)

            actual = {
                "steps": total_steps,
                "workouts": total_workouts,
                "minutes": total_minutes
            }

            level = p.fitness_level or "low"
            goal = DecisionTreeEngine.assign_goal(level)

            progress = DecisionTreeEngine.evaluate_progress(actual, goal)

            results[p.id] = {
                "fitness_level": level,
                "progress": progress
            }

        return results

    # ==============================
    # 7. LEADERBOARD (AI BASED)
    # ==============================
    @staticmethod
    def generate_leaderboard():
        participants = Participant.query.all()
        leaderboard = []

        for p in participants:
            user = User.query.get(p.user_id)
            activities = Activity.query.filter_by(participant_id=p.id).all()

            total_steps = sum(a.steps for a in activities)
            total_workouts = sum(a.workouts for a in activities)
            total_minutes = sum(a.active_minutes for a in activities)

            score = DecisionTreeEngine.calculate_score(
                total_steps,
                total_workouts,
                total_minutes
            )

            leaderboard.append({
                "username": user.username if user else "Unknown",
                "fitness_level": p.fitness_level,
                "score": round(score, 2)
            })

        leaderboard.sort(key=lambda x: x["score"], reverse=True)

        return leaderboard