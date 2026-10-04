
import time
import html

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.forecasting.forecast_engine import ForecastEngine
from src.ui.layout import page_header, ai_insight, page_footer


st.set_page_config(
    page_title="Previsão de Negócios com IA",
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
    "📈 Previsão de Negócios com IA",
    "Projete métricas do negócio, valide o desempenho dos "
    "modelos, compare cenários e apoie um planejamento "
    "baseado em evidências.",
)

st.markdown(
    """
    <div class="forecast-hero">
        <div class="forecast-title">
            🔮 Central de Inteligência de Previsões
        </div>
        <div class="forecast-subtitle">
            Explore o desempenho histórico, compare modelos
            de previsão, teste-os com observações reservadas e
            exporte projeções futuras para o planejamento do negócio.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# DATASET VALIDATION
# ---------------------------------------------------------
if "dataset" not in st.session_state:
    st.warning("Envie um dataset antes de gerar previsões.")
    st.info("Abra Enviar Dataset e carregue os dados do seu negócio.")
    st.stop()

df = st.session_state["dataset"]
filename = st.session_state.get("filename", "Dataset enviado")

if not isinstance(df, pd.DataFrame) or df.empty:
    st.error("O dataset enviado está vazio ou é inválido.")
    st.stop()

numeric_columns = [
    column
    for column in df.columns
    if pd.api.types.is_numeric_dtype(df[column])
]

if not numeric_columns:
    st.error("Não há colunas numéricas disponíveis para previsão.")
    st.stop()

st.success(f"Dataset ativo: {filename}")


# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------
st.markdown(
    '<div class="forecast-section">⚙️ Configuração da Previsão</div>',
    unsafe_allow_html=True,
)

cfg1, cfg2, cfg3 = st.columns([2, 1, 1])

with cfg1:
    target = st.selectbox(
        "Métrica de negócio",
        numeric_columns,
        key="forecast_target",
        help="Escolha vendas, receita, demanda, lucro ou outra métrica numérica.",
    )

with cfg2:
    periods = st.slider(
        "Períodos futuros",
        min_value=5,
        max_value=100,
        value=30,
        step=5,
        key="forecast_periods",
    )

with cfg3:
    selected_model = st.selectbox(
        "Modelo de previsão",
        ForecastEngine.AVAILABLE_MODELS,
        key="forecast_model",
    )

test_fraction = st.slider(
    "Fração de validação histórica",
    min_value=0.10,
    max_value=0.40,
    value=0.20,
    step=0.05,
    help="A parte mais recente das observações históricas é reservada para validação.",
)

raw_history = pd.to_numeric(df[target], errors="coerce")
raw_values = raw_history.to_numpy(dtype=float)
valid_mask = np.isfinite(raw_values)

history = pd.Series(
    raw_values[valid_mask],
    name=target,
).reset_index(drop=True)

if len(history) < 5:
    st.error("São necessárias pelo menos cinco observações numéricas válidas.")
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

m1.metric("Observações válidas", f"{len(history):,}")
m2.metric("Último valor", f"{latest_value:,.2f}")
m3.metric("Média recente", f"{recent_mean:,.2f}")
m4.metric("Horizonte da previsão", f"{periods} períodos")

st.caption(
    "Os períodos da previsão seguem a ordem das linhas. Eles não "
    "são interpretados automaticamente como dias, semanas ou meses."
)


# ---------------------------------------------------------
# MODEL VALIDATION
# ---------------------------------------------------------
st.markdown(
    '<div class="forecast-section">🧪 Validação Histórica do Modelo</div>',
    unsafe_allow_html=True,
)

st.write(
    "A validação treina com as observações mais antigas e testa "
    "com as mais recentes. Isso gera um teste ordenado no tempo "
    "mais realista do que embaralhar a série temporal."
)

run_evaluation = st.button(
    "🧪 Avaliar o modelo selecionado",
    width="stretch",
)

if run_evaluation:
    try:
        engine = ForecastEngine()

        with st.spinner("Avaliando o modelo nas observações reservadas..."):
            evaluation = engine.evaluate(
                df,
                target,
                test_size=test_fraction,
                model_name=selected_model,
            )

        actual = np.asarray(evaluation["actual"], dtype=float)
        predicted = np.asarray(evaluation["predicted"], dtype=float)

        evaluation_df = pd.DataFrame({
            "Observação": np.arange(
                len(history) - len(actual) + 1,
                len(history) + 1,
            ),
            "Real": actual,
            "Previsto": predicted,
            "Erro Absoluto": np.abs(actual - predicted),
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
        st.success("Validação histórica concluída.")

    except Exception as exc:
        st.error(f"Falha na avaliação do modelo: {exc}")

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
        f"Observações de treino: {metrics['train_observations']:,} "
        f"· Observações de validação: {metrics['test_observations']:,}"
    )

    fig_eval = go.Figure()
    fig_eval.add_trace(go.Scatter(
        x=evaluation_df["Observação"],
        y=evaluation_df["Real"],
        mode="lines+markers",
        name="Real",
    ))
    fig_eval.add_trace(go.Scatter(
        x=evaluation_df["Observação"],
        y=evaluation_df["Previsto"],
        mode="lines+markers",
        name="Previsto",
        line=dict(dash="dash"),
    ))
    fig_eval.update_layout(
        title="Real vs Previsto — Validação com Holdout",
        xaxis_title="Observação",
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
        "📥 Baixar resultados da validação",
        data=evaluation_df.to_csv(index=False).encode("utf-8"),
        file_name="forecast_validation.csv",
        mime="text/csv",
        width="stretch",
    )
elif run_evaluation is False:
    st.info(
        "Execute a validação para examinar os erros históricos "
        "antes de confiar na previsão futura."
    )


# ---------------------------------------------------------
# FORECAST GENERATION
# ---------------------------------------------------------
st.divider()
st.markdown(
    '<div class="forecast-section">🚀 Gerar Previsão Futura</div>',
    unsafe_allow_html=True,
)

generate = st.button(
    "🚀 Gerar previsão de negócio",
    type="primary",
    width="stretch",
)

if generate:
    start_time = time.perf_counter()

    try:
        engine = ForecastEngine()

        with st.spinner("Gerando predições futuras..."):
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
                f"Eram esperadas {periods} predições, "
                f"mas foram recebidas {len(predictions)}."
            )

        if not np.isfinite(predictions).all():
            raise ValueError("A previsão contém valores numéricos inválidos.")

        forecast_df = pd.DataFrame({
            "Período": np.arange(1, periods + 1),
            "Previsão": predictions,
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

        st.success("Previsão gerada com sucesso.")

    except Exception as exc:
        st.error(f"Falha ao gerar a previsão: {exc}")
        st.info(
            "Verifique a coluna-alvo e o motor de previsão. Se "
            "o problema continuar, compartilhe a mensagem de erro "
            "completa."
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
        "Praticamente estável"
        if np.isclose(absolute_change, 0, atol=1e-9)
        else "Crescente"
        if absolute_change > 0
        else "Decrescente"
    )

    st.divider()
    st.markdown(
        '<div class="forecast-section">📊 Resumo da Previsão para Decisão</div>',
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
        forecast_card("Previsão final", f"{final_forecast:,.2f}")
    with k2:
        forecast_card("Direção esperada", trend)
    with k3:
        forecast_card(
            "Variação vs último valor",
            f"{percentage_change:+.2f}%"
            if percentage_change is not None
            else "N/D — base zero",
        )
    with k4:
        forecast_card("Média da previsão", f"{forecast_mean:,.2f}")

    st.caption(f"Modelo usado: {result['model']}")

    # Historical versus forecast chart
    st.markdown(
        '<div class="forecast-section">📈 Histórico vs Previsão</div>',
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
        name="Histórico",
    ))

    forecast_x = np.arange(
        len(history),
        len(history) + periods,
    )

    fig.add_trace(go.Scatter(
        x=np.concatenate(([len(history) - 1], forecast_x)),
        y=np.concatenate(([latest_value], predictions)),
        mode="lines+markers",
        name="Previsão",
        line=dict(dash="dash", width=3),
    ))

    fig.add_vline(
        x=len(history) - 1,
        line_dash="dot",
        annotation_text="Início da previsão",
    )

    fig.update_layout(
        title=f"{target}: Desempenho Histórico e Previsão",
        xaxis_title="Observação / período futuro",
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
        '<div class="forecast-section">📉 Estatísticas da Previsão</div>',
        unsafe_allow_html=True,
    )

    s1, s2, s3, s4 = st.columns(4)
    s1.metric("Mínimo", f"{forecast_min:,.2f}")
    s2.metric("Máximo", f"{forecast_max:,.2f}")
    s3.metric("Desvio padrão", f"{forecast_std:,.2f}")
    s4.metric("Primeira previsão", f"{first_forecast:,.2f}")

    st.caption(
        "O desvio padrão da previsão descreve a variação entre "
        "os valores previstos; não é um intervalo de confiança."
    )

    # Historical context
    st.markdown(
        '<div class="forecast-section">🧭 Contexto Histórico</div>',
        unsafe_allow_html=True,
    )

    h1, h2, h3 = st.columns(3)
    h1.metric("Média histórica", f"{historical_mean:,.2f}")
    h2.metric("Média recente", f"{recent_mean:,.2f}")
    h3.metric(
        "Variabilidade histórica (CV)",
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
            f"A média recente está {recent_difference:+.2f}% em "
            "relação à média histórica."
        )

    # Scenario analysis: transparent arithmetic scenarios.
    st.markdown(
        '<div class="forecast-section">🧭 Análise de Cenários de Negócio</div>',
        unsafe_allow_html=True,
    )

    st.write(
        "Explore ajustes simples na previsão. São cenários ilustrativos, "
        "não predições treinadas separadamente."
    )

    adjustment = st.slider(
        "Ajuste do cenário (%)",
        min_value=-30,
        max_value=30,
        value=0,
        step=5,
        key="forecast_scenario_adjustment",
    )

    scenario_values = predictions * (1 + adjustment / 100)

    scenario_df = forecast_df.copy()
    scenario_df["Cenário"] = scenario_values

    sc1, sc2, sc3 = st.columns(3)
    sc1.metric("Previsão final base", f"{final_forecast:,.2f}")
    sc2.metric("Valor final do cenário", f"{scenario_values[-1]:,.2f}")
    sc3.metric(
        "Ajuste do cenário",
        f"{adjustment:+d}%",
    )

    fig_scenario = go.Figure()
    fig_scenario.add_trace(go.Scatter(
        x=forecast_df["Período"],
        y=predictions,
        mode="lines+markers",
        name="Previsão base",
    ))
    fig_scenario.add_trace(go.Scatter(
        x=forecast_df["Período"],
        y=scenario_values,
        mode="lines+markers",
        name="Cenário ajustado",
        line=dict(dash="dash"),
    ))
    fig_scenario.update_layout(
        title="Previsão Base vs Cenário Ilustrativo",
        xaxis_title="Período futuro",
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
        '<div class="forecast-section">📋 Resultados da Previsão</div>',
        unsafe_allow_html=True,
    )

    st.dataframe(
        scenario_df.style.format({
            "Previsão": "{:,.2f}",
            "Cenário": "{:,.2f}",
        }),
        width="stretch",
        hide_index=True,
    )

    d1, d2 = st.columns(2)

    with d1:
        st.download_button(
            "📥 Baixar CSV da previsão",
            data=forecast_df.to_csv(index=False).encode("utf-8"),
            file_name=f"{target.replace(' ', '_')}_forecast.csv",
            mime="text/csv",
            width="stretch",
        )

    with d2:
        st.download_button(
            "📥 Baixar CSV do cenário",
            data=scenario_df.to_csv(index=False).encode("utf-8"),
            file_name=f"{target.replace(' ', '_')}_scenario.csv",
            mime="text/csv",
            width="stretch",
        )

    st.markdown(
        '<div class="forecast-section">🤖 Interpretação da Previsão pela IA</div>',
        unsafe_allow_html=True,
    )

    change_text = (
        f"{percentage_change:+.2f}%"
        if percentage_change is not None
        else "não calculável a partir de uma base zero"
    )

    st.markdown(
        f"""
        <div class="forecast-note">
            <b>Alvo da previsão:</b> {html.escape(str(target))}<br><br>
            <b>Modelo selecionado:</b> {html.escape(str(result['model']))}<br><br>
            <b>Horizonte da previsão:</b> {periods} observações<br><br>
            <b>Último valor histórico:</b> {latest_value:,.2f}<br><br>
            <b>Valor final previsto:</b> {final_forecast:,.2f}<br><br>
            <b>Variação em relação à última observação:</b> {change_text}<br><br>
            <b>Direção esperada:</b> {trend}
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.warning(
        "Previsões são estimativas, não garantias. A Regressão Linear "
        "extrapola uma tendência em linha reta. O Random Forest geralmente "
        "não extrapola de forma confiável além dos valores aprendidos. "
        "Valide com observações históricas antes de usar os resultados "
        "em decisões importantes."
    )

    st.caption(
        f"Gerado em {result['generated_at']} · Tempo de "
        f"cálculo: {result['elapsed']:.2f} segundos"
    )

else:
    st.markdown(
        """
        <div class="forecast-note">
            <b>Pronto para prever?</b><br><br>
            Selecione uma métrica e um modelo de previsão, execute a
            validação histórica e depois gere uma previsão futura.
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------
# SHARED INSIGHTS AND NAVIGATION
# ---------------------------------------------------------
ai_insight(
    "Compare as previsões com os resultados reais regularmente. "
    "Revise os erros de validação, o contexto do negócio, a sazonalidade "
    "e os fatores externos antes de tomar decisões baseadas nas "
    "predições dos modelos."
)

st.divider()

nav_left, nav_right = st.columns(2)

with nav_left:
    if st.button("← Anterior: AutoML", width="stretch"):
        st.switch_page("pages/5_AutoML.py")

with nav_right:
    if st.button("Próximo: Predição →", width="stretch"):
        st.switch_page("pages/7_Prediction.py")

page_footer()
