from time import perf_counter

from pandas.api.types import is_numeric_dtype

from sklearn.ensemble import (
    RandomForestClassifier,
    RandomForestRegressor,
    GradientBoostingClassifier,
    GradientBoostingRegressor,
)
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.metrics import accuracy_score, r2_score


class AutoMLEngine:
    def __init__(self):
        self.problem_type = None
        self.best_model = None
        self.training_times = {}
        self.results = {}

    def compare_models(self, X_train, X_test, y_train, y_test):
        self.best_model = None
        self.training_times = {}
        self.results = {}

        # Preserve the existing automatic task detection.
        if not is_numeric_dtype(y_train) or y_train.nunique() <= 20:
            self.problem_type = "classification"

            models = {
                "Random Forest": RandomForestClassifier(
                    n_estimators=50,
                    max_depth=12,
                    min_samples_leaf=2,
                    n_jobs=-1,
                    random_state=42,
                ),
                "Decision Tree": DecisionTreeClassifier(
                    max_depth=12,
                    min_samples_leaf=2,
                    random_state=42,
                ),
                "Logistic Regression": LogisticRegression(
                    max_iter=300,
                    random_state=42,
                ),
                "Gradient Boosting": GradientBoostingClassifier(
                    n_estimators=30,
                    max_depth=2,
                    random_state=42,
                ),
            }
        else:
            self.problem_type = "regression"

            models = {
                "Random Forest": RandomForestRegressor(
                    n_estimators=50,
                    max_depth=12,
                    min_samples_leaf=2,
                    n_jobs=-1,
                    random_state=42,
                ),
                "Decision Tree": DecisionTreeRegressor(
                    max_depth=12,
                    min_samples_leaf=2,
                    random_state=42,
                ),
                "Linear Regression": LinearRegression(),
                "Gradient Boosting": GradientBoostingRegressor(
                    n_estimators=30,
                    max_depth=2,
                    random_state=42,
                ),
            }

        best_score = float("-inf")

        for name, model in models.items():
            started = perf_counter()

            model.fit(X_train, y_train)
            prediction = model.predict(X_test)

            elapsed = round(perf_counter() - started, 2)
            self.training_times[name] = elapsed

            if self.problem_type == "classification":
                score = accuracy_score(y_test, prediction) * 100
            else:
                score = r2_score(y_test, prediction) * 100

            score = round(float(score), 2)
            self.results[name] = score

            if score > best_score:
                best_score = score
                self.best_model = model

        return self.results

    def feature_importance(self, feature_names):
        if self.best_model is None:
            return None

        if hasattr(self.best_model, "feature_importances_"):
            importance = self.best_model.feature_importances_
            return dict(zip(feature_names, importance))

        return None
