
import time
import html

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.forecasting.forecast_engine import ForecastEngine
from src.ui.layout import page_header, ai_insight, page_footer


st.set_page_config(
    page_title="AI Business Forecasting",
    page_icon="📈",
    layout="wide",
)

MAX_CHART_POINTS = 2000


# ---------------------------------------------------------
# PROFESSIONAL UI
# ---------------------------------------------------------
st.markdown(
    """
    <style>
    .forecast-hero {
        padding: 1.5rem;
        border-radius: 18px;
        background: linear-gradient(
            135deg,
            rgba(30, 64, 175, 0.15),
            rgba(14, 116, 144, 0.10)
        );
        border: 1px solid rgba(100,116,139,0.25);
        margin-bottom: 1rem;
    }
    .forecast-title {
        font-size: 1.8rem;
        font-weight: 800;
        margin-bottom: 0.4rem;
    }
    .forecast-subtitle {
        color: #64748b;
        line-height: 1.6;
    }
    .forecast-card {
        padding: 1rem;
        border-radius: 14px;
        background: rgba(59,130,246,0.09);
        border: 1px solid rgba(59,130,246,0.2);
        min-height: 100px;
    }
    .forecast-card-label {
        font-size: 0.85rem;
        font-weight: 650;
        color: #64748b;
    }
    .forecast-card-value {
        font-size: 1.4rem;
        font-weight: 800;
        margin-top: 0.4rem;
        overflow-wrap: anywhere;
    }
    .forecast-section {
        font-size: 1.3rem;
        font-weight: 800;
        margin: 1rem 0 0.7rem;
    }
    .forecast-note {
        padding: 1rem;
        border-radius: 12px;
        background: rgba(14,116,144,0.08);
        border: 1px solid rgba(14,116,144,0.2);
        line-height: 1.7;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


page_header(
    "📈 AI Business Forecasting",
    "Forecast business metrics, validate model performance, "
    "compare scenarios, and support evidence-based planning.",
)

st.markdown(
    """
    <div class="forecast-hero">
        <div class="forecast-title">
            🔮 Business Forecast Intelligence Center
        </div>
        <div class="forecast-subtitle">
            Explore historical performance, compare forecasting
            models, test them against held-out observations, and
            export future projections for business planning.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# DATASET VALIDATION
# ---------------------------------------------------------
if "dataset" not in st.session_state:
    st.warning("Please upload a dataset before forecasting.")
    st.info("Open Upload Dataset and load your business data.")
    st.stop()

df = st.session_state["dataset"]
filename = st.session_state.get("filename", "Uploaded Dataset")

if not isinstance(df, pd.DataFrame) or df.empty:
    st.error("The uploaded dataset is empty or invalid.")
    st.stop()

numeric_columns = [
    column
    for column in df.columns
    if pd.api.types.is_numeric_dtype(df[column])
]

if not numeric_columns:
    st.error("No numeric columns are available for forecasting.")
    st.stop()

st.success(f"Active dataset: {filename}")


# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------
st.markdown(
    '<div class="forecast-section">⚙️ Forecast Configuration</div>',
    unsafe_allow_html=True,
)

cfg1, cfg2, cfg3 = st.columns([2, 1, 1])

with cfg1:
    target = st.selectbox(
        "Business metric",
        numeric_columns,
        key="forecast_target",
        help="Choose sales, revenue, demand, profit, or another numeric metric.",
    )

with cfg2:
    periods = st.slider(
        "Future periods",
        min_value=5,
        max_value=100,
        value=30,
        step=5,
        key="forecast_periods",
    )

with cfg3:
    selected_model = st.selectbox(
        "Forecasting model",
        ForecastEngine.AVAILABLE_MODELS,
        key="forecast_model",
    )

test_fraction = st.slider(
    "Historical validation fraction",
    min_value=0.10,
    max_value=0.40,
    value=0.20,
    step=0.05,
    help="The latest portion of historical observations is held out for validation.",
)

raw_history = pd.to_numeric(df[target], errors="coerce")
raw_values = raw_history.to_numpy(dtype=float)
valid_mask = np.isfinite(raw_values)

history = pd.Series(
    raw_values[valid_mask],
    name=target,
).reset_index(drop=True)

if len(history) < 5:
    st.error("At least five valid numeric observations are required.")
    st.stop()

latest_value = float(history.iloc[-1])
recent = history.tail(min(12, len(history)))
recent_mean = float(recent.mean())
historical_mean = float(history.mean())
historical_std = float(history.std()) if len(history) > 1 else 0.0

historical_cv = (
    abs(historical_std / historical_mean) * 100
    if not np.isclose(historical_mean, 0)
    else None
)

# Include the target data in the signature so changing datasets
# invalidates stale results even if the filename and shape stay the same.
dataset_signature = (
    filename,
    tuple(map(str, df.columns)),
    len(df),
    tuple(np.nan_to_num(
        raw_values,
        nan=9.87654321e99,
        posinf=8.7654321e99,
        neginf=-8.7654321e99,
    ).round(8).tolist()),
)

config_signature = (
    dataset_signature,
    target,
    periods,
    selected_model,
    test_fraction,
)

m1, m2, m3, m4 = st.columns(4)

m1.metric("Valid observations", f"{len(history):,}")
m2.metric("Latest value", f"{latest_value:,.2f}")
m3.metric("Recent average", f"{recent_mean:,.2f}")
m4.metric("Forecast horizon", f"{periods} periods")

st.caption(
    "Forecast periods follow row order. They are not automatically "
    "interpreted as days, weeks, or months."
)


# ---------------------------------------------------------
# MODEL VALIDATION
# ---------------------------------------------------------
st.markdown(
    '<div class="forecast-section">🧪 Historical Model Validation</div>',
    unsafe_allow_html=True,
)

st.write(
    "Validation trains on earlier observations and tests on later "
    "observations. This provides a more realistic time-ordered test "
    "than randomly shuffling a time series."
)

run_evaluation = st.button(
    "🧪 Evaluate Selected Model",
    width="stretch",
)

if run_evaluation:
    try:
        engine = ForecastEngine()

        with st.spinner("Evaluating model on held-out observations..."):
            evaluation = engine.evaluate(
                df,
                target,
                test_size=test_fraction,
                model_name=selected_model,
            )

        actual = np.asarray(evaluation["actual"], dtype=float)
        predicted = np.asarray(evaluation["predicted"], dtype=float)

        evaluation_df = pd.DataFrame({
            "Observation": np.arange(
                len(history) - len(actual) + 1,
                len(history) + 1,
            ),
            "Actual": actual,
            "Predicted": predicted,
            "Absolute Error": np.abs(actual - predicted),
        })

        st.session_state["business_forecast_evaluation"] = {
            "signature": config_signature,
            "metrics": {
                "mae": evaluation["mae"],
                "rmse": evaluation["rmse"],
                "mape": evaluation["mape"],
                "train_observations": evaluation["train_observations"],
                "test_observations": evaluation["test_observations"],
            },
            "evaluation_df": evaluation_df,
        }
        st.success("Historical validation completed.")

    except Exception as exc:
        st.error(f"Model evaluation failed: {exc}")

evaluation_result = st.session_state.get(
    "business_forecast_evaluation"
)

if (
    evaluation_result is not None
    and evaluation_result["signature"] == config_signature
):
    metrics = evaluation_result["metrics"]
    evaluation_df = evaluation_result["evaluation_df"]

    e1, e2, e3 = st.columns(3)
    e1.metric("MAE", f"{metrics['mae']:,.4f}")
    e2.metric("RMSE", f"{metrics['rmse']:,.4f}")
    e3.metric(
        "MAPE",
        f"{metrics['mape']:.2f}%"
        if metrics["mape"] is not None
        else "N/A",
    )

    st.caption(
        f"Training observations: {metrics['train_observations']:,} · "
        f"Validation observations: {metrics['test_observations']:,}"
    )

    fig_eval = go.Figure()
    fig_eval.add_trace(go.Scatter(
        x=evaluation_df["Observation"],
        y=evaluation_df["Actual"],
        mode="lines+markers",
        name="Actual",
    ))
    fig_eval.add_trace(go.Scatter(
        x=evaluation_df["Observation"],
        y=evaluation_df["Predicted"],
        mode="lines+markers",
        name="Predicted",
        line=dict(dash="dash"),
    ))
    fig_eval.update_layout(
        title="Actual vs Predicted — Holdout Validation",
        xaxis_title="Observation",
        yaxis_title=target,
        height=400,
        hovermode="x unified",
        margin=dict(l=20, r=20, t=55, b=20),
    )
    st.plotly_chart(
        fig_eval,
        width="stretch",
        config={"displaylogo": False},
    )

    st.download_button(
        "📥 Download Validation Results",
        data=evaluation_df.to_csv(index=False).encode("utf-8"),
        file_name="forecast_validation.csv",
        mime="text/csv",
        width="stretch",
    )
elif run_evaluation is False:
    st.info(
        "Run validation to inspect historical errors before relying "
        "on the future forecast."
    )


# ---------------------------------------------------------
# FORECAST GENERATION
# ---------------------------------------------------------
st.divider()
st.markdown(
    '<div class="forecast-section">🚀 Generate Future Forecast</div>',
    unsafe_allow_html=True,
)

generate = st.button(
    "🚀 Generate Business Forecast",
    type="primary",
    width="stretch",
)

if generate:
    start_time = time.perf_counter()

    try:
        engine = ForecastEngine()

        with st.spinner("Generating future predictions..."):
            raw_prediction = engine.forecast(
                df,
                target,
                periods,
                model_name=selected_model,
            )

        predictions = np.asarray(
            raw_prediction,
            dtype=float,
        ).reshape(-1)

        if len(predictions) != periods:
            raise ValueError(
                f"Expected {periods} predictions, "
                f"received {len(predictions)}."
            )

        if not np.isfinite(predictions).all():
            raise ValueError("The forecast contains invalid numeric values.")

        forecast_df = pd.DataFrame({
            "Period": np.arange(1, periods + 1),
            "Forecast": predictions,
        })

        elapsed = time.perf_counter() - start_time

        st.session_state["business_forecast_result"] = {
            "signature": config_signature,
            "target": target,
            "periods": periods,
            "model": selected_model,
            "forecast_df": forecast_df,
            "predictions": predictions.tolist(),
            "elapsed": elapsed,
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        }

        st.success("Forecast generated successfully.")

    except Exception as exc:
        st.error(f"Forecast generation failed: {exc}")
        st.info(
            "Check the target column and the forecasting engine. "
            "If the problem continues, share the full error message."
        )


# ---------------------------------------------------------
# FORECAST RESULTS
# ---------------------------------------------------------
result = st.session_state.get("business_forecast_result")

if result is not None and result["signature"] == config_signature:
    forecast_df = result["forecast_df"]
    predictions = np.asarray(result["predictions"], dtype=float)

    first_forecast = float(predictions[0])
    final_forecast = float(predictions[-1])
    forecast_mean = float(np.mean(predictions))
    forecast_min = float(np.min(predictions))
    forecast_max = float(np.max(predictions))
    forecast_std = float(np.std(predictions))

    absolute_change = final_forecast - latest_value
    percentage_change = (
        absolute_change / abs(latest_value) * 100
        if not np.isclose(latest_value, 0)
        else None
    )

    trend = (
        "Broadly stable"
        if np.isclose(absolute_change, 0, atol=1e-9)
        else "Increasing"
        if absolute_change > 0
        else "Decreasing"
    )

    st.divider()
    st.markdown(
        '<div class="forecast-section">📊 Forecast Decision Summary</div>',
        unsafe_allow_html=True,
    )

    def forecast_card(label, value):
        st.markdown(
            f"""
            <div class="forecast-card">
                <div class="forecast-card-label">{html.escape(label)}</div>
                <div class="forecast-card-value">{html.escape(str(value))}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    k1, k2, k3, k4 = st.columns(4)

    with k1:
        forecast_card("Final forecast", f"{final_forecast:,.2f}")
    with k2:
        forecast_card("Expected direction", trend)
    with k3:
        forecast_card(
            "Change vs latest",
            f"{percentage_change:+.2f}%"
            if percentage_change is not None
            else "N/A — zero baseline",
        )
    with k4:
        forecast_card("Forecast average", f"{forecast_mean:,.2f}")

    st.caption(f"Model used: {result['model']}")

    # Historical versus forecast chart
    st.markdown(
        '<div class="forecast-section">📈 Historical vs Forecast</div>',
        unsafe_allow_html=True,
    )

    if len(history) > MAX_CHART_POINTS:
        chart_indices = np.linspace(
            0, len(history) - 1, MAX_CHART_POINTS, dtype=int
        )
        historical_chart = history.iloc[chart_indices]
    else:
        historical_chart = history

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=historical_chart.index,
        y=historical_chart.values,
        mode="lines",
        name="Historical",
    ))

    forecast_x = np.arange(
        len(history),
        len(history) + periods,
    )

    fig.add_trace(go.Scatter(
        x=np.concatenate(([len(history) - 1], forecast_x)),
        y=np.concatenate(([latest_value], predictions)),
        mode="lines+markers",
        name="Forecast",
        line=dict(dash="dash", width=3),
    ))

    fig.add_vline(
        x=len(history) - 1,
        line_dash="dot",
        annotation_text="Forecast starts",
    )

    fig.update_layout(
        title=f"{target}: Historical Performance and Forecast",
        xaxis_title="Observation / future period",
        yaxis_title=target,
        height=470,
        hovermode="x unified",
        margin=dict(l=20, r=20, t=60, b=20),
    )

    st.plotly_chart(
        fig,
        width="stretch",
        config={"displaylogo": False},
    )

    # Forecast statistics
    st.markdown(
        '<div class="forecast-section">📉 Forecast Statistics</div>',
        unsafe_allow_html=True,
    )

    s1, s2, s3, s4 = st.columns(4)
    s1.metric("Minimum", f"{forecast_min:,.2f}")
    s2.metric("Maximum", f"{forecast_max:,.2f}")
    s3.metric("Standard deviation", f"{forecast_std:,.2f}")
    s4.metric("First forecast", f"{first_forecast:,.2f}")

    st.caption(
        "Forecast standard deviation describes variation between "
        "forecast values; it is not a confidence interval."
    )

    # Historical context
    st.markdown(
        '<div class="forecast-section">🧭 Historical Context</div>',
        unsafe_allow_html=True,
    )

    h1, h2, h3 = st.columns(3)
    h1.metric("Historical average", f"{historical_mean:,.2f}")
    h2.metric("Recent average", f"{recent_mean:,.2f}")
    h3.metric(
        "Historical variability (CV)",
        f"{historical_cv:.2f}%"
        if historical_cv is not None
        else "N/A",
    )

    if not np.isclose(historical_mean, 0):
        recent_difference = (
            (recent_mean - historical_mean)
            / abs(historical_mean)
        ) * 100

        st.info(
            f"Recent average is {recent_difference:+.2f}% relative "
            "to the historical average."
        )

    # Scenario analysis: transparent arithmetic scenarios.
    st.markdown(
        '<div class="forecast-section">🧭 Business Scenario Analysis</div>',
        unsafe_allow_html=True,
    )

    st.write(
        "Explore simple adjustments to the forecast. These are "
        "illustrative scenarios, not separately trained predictions."
    )

    adjustment = st.slider(
        "Scenario adjustment (%)",
        min_value=-30,
        max_value=30,
        value=0,
        step=5,
        key="forecast_scenario_adjustment",
    )

    scenario_values = predictions * (1 + adjustment / 100)

    scenario_df = forecast_df.copy()
    scenario_df["Scenario"] = scenario_values

    sc1, sc2, sc3 = st.columns(3)
    sc1.metric("Base final forecast", f"{final_forecast:,.2f}")
    sc2.metric("Scenario final value", f"{scenario_values[-1]:,.2f}")
    sc3.metric(
        "Scenario adjustment",
        f"{adjustment:+d}%",
    )

    fig_scenario = go.Figure()
    fig_scenario.add_trace(go.Scatter(
        x=forecast_df["Period"],
        y=predictions,
        mode="lines+markers",
        name="Base forecast",
    ))
    fig_scenario.add_trace(go.Scatter(
        x=forecast_df["Period"],
        y=scenario_values,
        mode="lines+markers",
        name="Adjusted scenario",
        line=dict(dash="dash"),
    ))
    fig_scenario.update_layout(
        title="Base Forecast vs Illustrative Scenario",
        xaxis_title="Future period",
        yaxis_title=target,
        height=390,
        margin=dict(l=20, r=20, t=55, b=20),
    )
    st.plotly_chart(
        fig_scenario,
        width="stretch",
        config={"displaylogo": False},
    )

    # Forecast results and downloads
    st.markdown(
        '<div class="forecast-section">📋 Forecast Results</div>',
        unsafe_allow_html=True,
    )

    st.dataframe(
        scenario_df.style.format({
            "Forecast": "{:,.2f}",
            "Scenario": "{:,.2f}",
        }),
        width="stretch",
        hide_index=True,
    )

    d1, d2 = st.columns(2)

    with d1:
        st.download_button(
            "📥 Download Forecast CSV",
            data=forecast_df.to_csv(index=False).encode("utf-8"),
            file_name=f"{target.replace(' ', '_')}_forecast.csv",
            mime="text/csv",
            width="stretch",
        )

    with d2:
        st.download_button(
            "📥 Download Scenario CSV",
            data=scenario_df.to_csv(index=False).encode("utf-8"),
            file_name=f"{target.replace(' ', '_')}_scenario.csv",
            mime="text/csv",
            width="stretch",
        )

    st.markdown(
        '<div class="forecast-section">🤖 AI Forecast Interpretation</div>',
        unsafe_allow_html=True,
    )

    change_text = (
        f"{percentage_change:+.2f}%"
        if percentage_change is not None
        else "not calculable from a zero baseline"
    )

    st.markdown(
        f"""
        <div class="forecast-note">
            <b>Forecast target:</b> {html.escape(str(target))}<br><br>
            <b>Selected model:</b> {html.escape(str(result['model']))}<br><br>
            <b>Forecast horizon:</b> {periods} observations<br><br>
            <b>Latest historical value:</b> {latest_value:,.2f}<br><br>
            <b>Final predicted value:</b> {final_forecast:,.2f}<br><br>
            <b>Change versus latest observation:</b> {change_text}<br><br>
            <b>Expected direction:</b> {trend}
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.warning(
        "Forecasts are estimates, not guarantees. Linear Regression "
        "extrapolates a straight-line trend. Random Forest generally "
        "does not extrapolate beyond learned target ranges reliably. "
        "Validate against historical observations before using results "
        "for important business decisions."
    )

    st.caption(
        f"Generated at {result['generated_at']} · "
        f"Computation time: {result['elapsed']:.2f} seconds"
    )

else:
    st.markdown(
        """
        <div class="forecast-note">
            <b>Ready to forecast?</b><br><br>
            Select a metric and forecasting model, run historical
            validation, then generate a future forecast.
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------
# SHARED INSIGHTS AND NAVIGATION
# ---------------------------------------------------------
ai_insight(
    "Compare forecasts with actual outcomes regularly. Review "
    "validation errors, business context, seasonality and external "
    "factors before making decisions based on model predictions."
)

st.divider()

nav_left, nav_right = st.columns(2)

with nav_left:
    if st.button("← Previous: AutoML", width="stretch"):
        st.switch_page("pages/5_AutoML.py")

with nav_right:
    if st.button("Next: Prediction →", width="stretch"):
        st.switch_page("pages/7_Prediction.py")

page_footer()
