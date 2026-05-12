class DecisionTreeEngine:

    # ==============================
    # 1. CALCULATE SCORE (IMPROVED)
    # ==============================
    @staticmethod
    def calculate_score(steps, workouts, minutes):
        """
        Weighted scoring system
        """
        step_weight = 0.1
        workout_weight = 10
        minute_weight = 0.5

        score = (steps * step_weight) + (workouts * workout_weight) + (minutes * minute_weight)
        return round(score, 2)

    # ==============================
    # 2. ASSIGN GOALS (SMART LOGIC)
    # ==============================
    @staticmethod
    def assign_goal(cluster_level):
        """
        Assign goals based on fitness level
        """
        if cluster_level == "low":
            return {
                "steps": 4000,
                "workouts": 2,
                "minutes": 25
            }

        elif cluster_level == "medium":
            return {
                "steps": 8000,
                "workouts": 4,
                "minutes": 45
            }

        elif cluster_level == "high":
            return {
                "steps": 12000,
                "workouts": 6,
                "minutes": 60
            }

        # fallback
        return {
            "steps": 5000,
            "workouts": 3,
            "minutes": 30
        }

    # ==============================
    # 3. SAFE DIVISION
    # ==============================
    @staticmethod
    def safe_divide(a, b):
        return a / b if b != 0 else 0

    # ==============================
    # 4. EVALUATE PROGRESS (IMPROVED)
    # ==============================
    @staticmethod
    def evaluate_progress(actual, goal):
        """
        Calculates percentage completion with weighted logic
        """

        # Individual scores
        step_score = min(DecisionTreeEngine.safe_divide(actual.get("steps", 0), goal.get("steps", 1)), 1)
        workout_score = min(DecisionTreeEngine.safe_divide(actual.get("workouts", 0), goal.get("workouts", 1)), 1)
        minute_score = min(DecisionTreeEngine.safe_divide(actual.get("minutes", 0), goal.get("minutes", 1)), 1)

        # Weighted importance
        step_weight = 0.4
        workout_weight = 0.3
        minute_weight = 0.3

        total = (
            (step_score * step_weight) +
            (workout_score * workout_weight) +
            (minute_score * minute_weight)
        )

        return round(total * 100, 2)

    # ==============================
    # 5. PERFORMANCE LEVEL (NEW)
    # ==============================
    @staticmethod
    def get_performance_level(progress):
        """
        Converts % into readable label
        """
        if progress >= 90:
            return "Excellent"
        elif progress >= 70:
            return "Good"
        elif progress >= 40:
            return "Average"
        else:
            return "Needs Improvement"