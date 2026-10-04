
import numpy as np
import pandas as pd

from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error


class ForecastEngine:
    """Forecast numeric time-series-like data using regression models."""

    AVAILABLE_MODELS = [
        "Linear Regression",
        "Random Forest",
    ]

    def _prepare_series(self, dataframe, target_column):
        if target_column not in dataframe.columns:
            raise ValueError(
                f"Target column '{target_column}' was not found."
            )

        series = pd.to_numeric(
            dataframe[target_column], errors="coerce"
        )

        values = series.to_numpy(dtype=float)
        values = values[np.isfinite(values)]

        if len(values) < 5:
            raise ValueError(
                "At least 5 valid numeric observations are required."
            )

        return values

    def _build_model(self, model_name):
        if model_name == "Linear Regression":
            return LinearRegression()

        if model_name == "Random Forest":
            return RandomForestRegressor(
                n_estimators=100,
                max_depth=8,
                random_state=42,
                n_jobs=-1,
            )

        raise ValueError(f"Unsupported forecasting model: {model_name}")

    def forecast(
        self,
        dataframe,
        target_column,
        periods=30,
        model_name="Linear Regression",
    ):
        """Generate future predictions using the selected model."""
        if not isinstance(periods, (int, np.integer)) or periods < 1:
            raise ValueError("Periods must be a positive integer.")

        y = self._prepare_series(dataframe, target_column)
        X = np.arange(len(y)).reshape(-1, 1)

        model = self._build_model(model_name)
        model.fit(X, y)

        future_x = np.arange(
            len(y), len(y) + periods
        ).reshape(-1, 1)

        predictions = np.asarray(
            model.predict(future_x), dtype=float
        ).reshape(-1)

        if len(predictions) != periods:
            raise ValueError("Unexpected number of forecast values.")

        if not np.isfinite(predictions).all():
            raise ValueError("Forecast contains invalid numeric values.")

        return predictions

    def evaluate(
        self,
        dataframe,
        target_column,
        test_size=0.2,
        model_name="Linear Regression",
    ):
        """Evaluate using a chronological holdout, not a random split."""
        y = self._prepare_series(dataframe, target_column)

        if not 0 < test_size < 1:
            raise ValueError("test_size must be between 0 and 1.")

        split = int(len(y) * (1 - test_size))
        split = max(3, min(split, len(y) - 1))

        train_y = y[:split]
        actual = y[split:]

        X_train = np.arange(split).reshape(-1, 1)
        X_test = np.arange(split, len(y)).reshape(-1, 1)

        model = self._build_model(model_name)
        model.fit(X_train, train_y)

        predicted = np.asarray(
            model.predict(X_test), dtype=float
        ).reshape(-1)

        mae = float(mean_absolute_error(actual, predicted))
        rmse = float(np.sqrt(mean_squared_error(actual, predicted)))

        nonzero = np.abs(actual) > 1e-10
        mape = (
            float(
                np.mean(
                    np.abs(
                        (actual[nonzero] - predicted[nonzero])
                        / actual[nonzero]
                    )
                ) * 100
            )
            if nonzero.any()
            else None
        )

        return {
            "model": model_name,
            "train_observations": len(train_y),
            "test_observations": len(actual),
            "actual": actual,
            "predicted": predicted,
            "mae": mae,
            "rmse": rmse,
            "mape": mape,
        }
