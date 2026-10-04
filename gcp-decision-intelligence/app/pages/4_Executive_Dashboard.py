import streamlit as st
import pandas as pd
import plotly.express as px

from src.ui.layout import page_header, ai_insight, page_footer
from src.ui.cards import kpi_card

from src.dashboard_ai.visualization_recommender import VisualizationRecommender
from src.database.database import Database


# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="Painel Executivo",
    page_icon="📊",
    layout="wide"
)


# ==========================================================
# PERFORMANCE SETTINGS
# ==========================================================

MAX_CHART_ROWS = 5000
MAX_CORRELATION_COLUMNS = 20


# ==========================================================
# CUSTOM CSS
# ==========================================================

st.markdown(
    """
    <style>
    .dashboard-hero {
        padding: 1.5rem 1.8rem;
        border-radius: 18px;
        background: linear-gradient(
            135deg,
            rgba(30, 64, 175, 0.12),
            rgba(14, 116, 144, 0.10)
        );
        border: 1px solid rgba(100, 116, 139, 0.18);
        margin-bottom: 1.2rem;
    }

    .dashboard-title {
        font-size: 2rem;
        font-weight: 800;
        margin-bottom: 0.3rem;
    }

    .dashboard-subtitle {
        color: #64748b;
        font-size: 1rem;
    }

    .status-card {
        padding: 1rem 1.2rem;
        border-radius: 14px;
        border: 1px solid rgba(100, 116, 139, 0.18);
        background: rgba(248, 250, 252, 0.65);
        margin-bottom: 0.7rem;
    }

    .status-title {
        font-weight: 700;
        font-size: 0.9rem;
    }

    .status-value {
        font-size: 1.35rem;
        font-weight: 800;
        margin-top: 0.2rem;
    }

    .action-card {
        padding: 1.2rem;
        border-radius: 16px;
        border: 1px solid rgba(100, 116, 139, 0.18);
        background: Black;
        min-height: 130px;
    }

    .action-title {
        font-size: 1rem;
        font-weight: 750;
        margin-bottom: 0.4rem;
    }

    .action-text {
        color: #cbd5e1;
        font-size: 0.9rem;
    }

    .performance-note {
        padding: 0.8rem 1rem;
        border-radius: 12px;
        background: rgba(14, 116, 144, 0.08);
        border: 1px solid rgba(14, 116, 144, 0.15);
        color: #475569;
        font-size: 0.88rem;
    }

    .section-label {
        font-size: 1.35rem;
        font-weight: 800;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# ==========================================================
# HEADER
# ==========================================================

page_header(
    "📊 Painel Executivo",
    "KPIs Executivos do Negócio, Insights de IA e Inteligência de Decisão"
)

st.markdown(
    """
    <div class="dashboard-hero">
        <div class="dashboard-title">🚀 Central Executiva de Decisão</div>
        <div class="dashboard-subtitle">
            Uma camada de business intelligence otimizada para
            monitorar a saúde dos dados, a atividade de IA, os padrões
            do negócio e as ações executivas.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# ==========================================================
# DATASET CHECK
# ==========================================================

if "dataset" not in st.session_state:
    st.warning("📂 Envie um dataset primeiro.")
    st.info("Vá em **Enviar Dataset** e envie o dataset do seu negócio.")
    st.stop()


df = st.session_state["dataset"]

filename = st.session_state.get(
    "filename",
    "Dataset enviado"
)


if df is None or df.empty:
    st.error("O dataset enviado está vazio.")
    st.stop()


# ==========================================================
# DATA PREPARATION
# ==========================================================

rows = len(df)
columns = len(df.columns)

numeric_cols = df.select_dtypes(
    include="number"
).columns.tolist()

cat_cols = df.select_dtypes(
    exclude="number"
).columns.tolist()


# ==========================================================
# CACHED DATA QUALITY CALCULATIONS
# ==========================================================

@st.cache_data(show_spinner=False)
def calculate_quality_metrics(dataframe):

    missing = int(
        dataframe.isnull().sum().sum()
    )

    duplicates = int(
        dataframe.duplicated().sum()
    )

    return missing, duplicates


missing, duplicates = calculate_quality_metrics(df)


# ==========================================================
# BUSINESS HEALTH SCORE
# ==========================================================

def calculate_health_score(
    missing_count,
    duplicate_count,
    total_rows,
    total_columns
):

    if total_rows == 0:
        return 0

    missing_rate = (
        missing_count /
        max(total_rows * max(total_columns, 1), 1)
    )

    duplicate_rate = (
        duplicate_count /
        max(total_rows, 1)
    )

    score = 100

    score -= min(
        int(missing_rate * 100),
        30
    )

    score -= min(
        int(duplicate_rate * 100),
        20
    )

    if total_columns < 3:
        score -= 10

    if total_rows < 100:
        score -= 10

    return max(
        min(score, 100),
        0
    )


score = calculate_health_score(
    missing,
    duplicates,
    rows,
    columns
)


if score >= 90:
    grade = "🟢 Excelente"
elif score >= 75:
    grade = "🟡 Bom"
elif score >= 60:
    grade = "🟠 Regular"
else:
    grade = "🔴 Requer atenção"


# ==========================================================
# DATABASE
# ==========================================================

@st.cache_resource
def get_database():
    return Database()


database = get_database()


@st.cache_data(show_spinner=False)
def load_database_activity():

    models_data = database.get_models()
    predictions_data = database.get_predictions()

    return models_data, predictions_data


try:

    models, predictions = load_database_activity()

except Exception:

    models = []
    predictions = []


# ==========================================================
# AI VISUALIZATION RECOMMENDER
# ==========================================================

@st.cache_data(show_spinner=False)
def get_visualization_recommendations(dataframe):

    recommender = VisualizationRecommender(
        dataframe
    )

    return recommender.recommend()


try:

    recommendations = get_visualization_recommendations(df)

except Exception:

    recommendations = []


# ==========================================================
# EXECUTIVE STATUS
# ==========================================================

st.markdown(
    '<div class="section-label">📌 Status Executivo</div>',
    unsafe_allow_html=True
)

c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    kpi_card(
        "Saúde do Negócio",
        f"{score}/100"
    )

with c2:
    kpi_card(
        "Registros",
        f"{rows:,}"
    )

with c3:
    kpi_card(
        "Variáveis",
        columns
    )

with c4:
    kpi_card(
        "Modelos de IA",
        len(models)
    )

with c5:
    kpi_card(
        "Predições",
        len(predictions)
    )


st.divider()


# ==========================================================
# HEALTH CENTER
# ==========================================================

st.markdown(
    '<div class="section-label">🏥 Saúde do Negócio e dos Dados</div>',
    unsafe_allow_html=True
)

health_left, health_right = st.columns(
    [2, 1]
)

with health_left:

    st.progress(
        score / 100
    )

    st.metric(
        "Saúde Geral dos Dados do Negócio",
        f"{score}/100"
    )

    st.caption(
        f"Dataset: {filename}"
    )


with health_right:

    st.metric(
        "Nota de Saúde",
        grade
    )

    st.metric(
        "Valores Ausentes",
        f"{missing:,}"
    )

    st.metric(
        "Linhas Duplicadas",
        f"{duplicates:,}"
    )


# ==========================================================
# AI DECISION STATUS
# ==========================================================

if score >= 90:

    decision_status = (
        "O dataset está em ótimas condições "
        "para analytics, modelagem e previsões."
    )

    decision_type = "🟢 Pronto para IA"

elif score >= 75:

    decision_status = (
        "O dataset é utilizável, mas é recomendável "
        "concluir o pré-processamento antes de decisões "
        "críticas."
    )

    decision_type = "🟡 Revisar antes da IA"

else:

    decision_status = (
        "Os problemas de qualidade dos dados "
        "devem ser resolvidos antes de confiar "
        "nos resultados preditivos."
    )

    decision_type = "🔴 Limpeza de dados necessária"


st.info(
    f"**{decision_type}** — {decision_status}"
)


# ==========================================================
# EXECUTIVE SNAPSHOT
# ==========================================================

st.markdown(
    '<div class="section-label">🎯 Retrato Executivo</div>',
    unsafe_allow_html=True
)

s1, s2, s3 = st.columns(3)

with s1:

    st.markdown(
        """
        <div class="action-card">
            <div class="action-title">📊 Base de Dados</div>
            <div class="action-text">
                Seu dataset contém atualmente as informações
                essenciais disponíveis para analytics de negócio,
                modelagem e apoio à decisão.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with s2:

    model_status = (
        f"{len(models)} modelo(s) treinado(s)"
        if len(models) > 0
        else "Nenhum modelo treinado ainda"
    )

    st.markdown(
        f"""
        <div class="action-card">
            <div class="action-title">🤖 Atividade de IA</div>
            <div class="action-text">
                {model_status}. Atividade de predição:
                {len(predictions)} execução(ões) de predição registrada(s).
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with s3:

    st.markdown(
        f"""
        <div class="action-card">
            <div class="action-title">🔎 Cobertura da Inteligência</div>
            <div class="action-text">
                {len(numeric_cols)} variáveis numéricas e
                {len(cat_cols)} variáveis categóricas detectadas.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


st.divider()


# ==========================================================
# AI ACTION CENTER
# ==========================================================

st.markdown(
    '<div class="section-label">🧠 Central de Ações Executivas da IA</div>',
    unsafe_allow_html=True
)

actions = []

if missing > 0:
    actions.append(
        (
            "⚠️ Tratar dados ausentes",
            f"{missing:,} valores ausentes detectados.",
            "Qualidade dos Dados"
        )
    )

if duplicates > 0:
    actions.append(
        (
            "🔁 Revisar registros duplicados",
            f"{duplicates:,} linhas duplicadas detectadas.",
            "Qualidade dos Dados"
        )
    )

if len(numeric_cols) >= 2:
    actions.append(
        (
            "📈 Explorar padrões preditivos",
            "Há várias variáveis numéricas disponíveis para modelagem.",
            "Machine Learning"
        )
    )

if len(cat_cols) > 0:
    actions.append(
        (
            "🎯 Analisar segmentos do negócio",
            "As dimensões categóricas permitem análises de segmentação.",
            "Business Intelligence"
        )
    )

if len(models) == 0:
    actions.append(
        (
            "🤖 Treinar seu primeiro modelo",
            "Nenhum modelo treinado registrado no momento.",
            "IA"
        )
    )

if len(predictions) == 0:
    actions.append(
        (
            "🔮 Gerar predições",
            "Nenhuma execução de predição registrada no momento.",
            "Predição"
        )
    )


if not actions:

    st.success(
        "✅ Nenhuma ação executiva imediata foi detectada."
    )

else:

    action_cols = st.columns(
        min(len(actions), 3)
    )

    for index, action in enumerate(actions[:3]):

        with action_cols[index]:

            title, description, category = action

            st.markdown(
                f"""
                <div class="action-card">
                    <div class="action-title">{title}</div>
                    <div class="action-text">
                        {description}
                    </div>
                    <br>
                    <small><b>Área:</b> {category}</small>
                </div>
                """,
                unsafe_allow_html=True
            )


st.divider()


# ==========================================================
# MODEL & PREDICTION ACTIVITY
# ==========================================================

st.markdown(
    '<div class="section-label">🤖 Atividade de IA</div>',
    unsafe_allow_html=True
)

activity_left, activity_right = st.columns(2)


with activity_left:

    st.subheader("Último Modelo")

    if len(models) > 0:

        latest_model = models[0]

        try:

            model_name = latest_model[2]
            performance = latest_model[3]
            problem_type = latest_model[4]

        except Exception:

            model_name = "Modelo registrado"
            performance = "-"
            problem_type = "-"

        m1, m2, m3 = st.columns(3)

        with m1:
            st.metric(
                "Modelo",
                model_name
            )

        with m2:
            try:
                st.metric(
                    "Desempenho",
                    f"{float(performance):.2f}"
                )
            except Exception:
                st.metric(
                    "Desempenho",
                    performance
                )

        with m3:
            st.metric(
                "Problema",
                problem_type
            )

    else:

        st.info(
            "Nenhum modelo treinado foi registrado ainda."
        )


with activity_right:

    st.subheader("Última Predição")

    if len(predictions) > 0:

        latest_prediction = predictions[0]

        try:

            prediction_model = latest_prediction[1]
            prediction_dataset = latest_prediction[2]
            prediction_rows = latest_prediction[3]

        except Exception:

            prediction_model = "Predição"
            prediction_dataset = filename
            prediction_rows = "-"

        p1, p2, p3 = st.columns(3)

        with p1:
            st.metric(
                "Modelo",
                prediction_model
            )

        with p2:
            st.metric(
                "Linhas",
                prediction_rows
            )

        with p3:
            st.metric(
                "Dataset",
                prediction_dataset
            )

    else:

        st.info(
            "Nenhuma atividade de predição foi registrada ainda."
        )


st.divider()


# ==========================================================
# PERFORMANCE OPTIMIZATION
# ==========================================================

st.markdown(
    '<div class="section-label">⚡ Desempenho das Visualizações</div>',
    unsafe_allow_html=True
)

st.markdown(
    f"""
    <div class="performance-note">
        <b>Modo de desempenho ativado.</b>
        Os cálculos de KPI usam o dataset completo.
        As visualizações usam automaticamente no máximo
        <b>{MAX_CHART_ROWS:,} linhas</b> quando o dataset é maior,
        reduzindo o tempo de renderização no navegador e no Plotly.
    </div>
    """,
    unsafe_allow_html=True
)


# ==========================================================
# CHART DATA PREPARATION
# ==========================================================

@st.cache_data(show_spinner=False)
def prepare_chart_data(dataframe, max_rows):

    if len(dataframe) <= max_rows:

        return dataframe.copy()

    return dataframe.sample(
        n=max_rows,
        random_state=42
    ).copy()


chart_df = prepare_chart_data(
    df,
    MAX_CHART_ROWS
)


# ==========================================================
# VISUALIZATION CENTER
# ==========================================================

st.markdown(
    '<div class="section-label">📊 Central de Inteligência de Visualização</div>',
    unsafe_allow_html=True
)

st.caption(
    "Os gráficos são gerados apenas quando você os seleciona. Isso "
    "evita renderizações desnecessárias do Plotly a cada carregamento "
    "da página."
)


visualization_options = [
    "📈 Análise de Distribuição",
    "🔥 Análise de Correlação",
    "🥧 Distribuição por Categoria",
    "📊 Categoria vs Numérico",
    "📦 Análise de Outliers",
    "📈 Análise de Tendência",
    "🌍 Análise Geográfica"
]


selected_visualization = st.selectbox(
    "Selecione a análise",
    visualization_options,
    key="executive_visualization"
)


# ==========================================================
# DISTRIBUTION
# ==========================================================

if selected_visualization == "📈 Análise de Distribuição":

    if len(numeric_cols) == 0:

        st.info(
            "Não há colunas numéricas disponíveis para a análise de distribuição."
        )

    else:

        column = st.selectbox(
            "Coluna numérica",
            numeric_cols,
            key="executive_histogram_column"
        )

        plot_df = chart_df[[column]].dropna()

        fig = px.histogram(
            plot_df,
            x=column,
            nbins=30,
            title=f"Distribuição de {column}"
        )

        fig.update_layout(
            height=450,
            margin=dict(l=20, r=20, t=60, b=20)
        )

        st.plotly_chart(
            fig,
            width="stretch",
            key="executive_histogram"
        )


# ==========================================================
# CORRELATION
# ==========================================================

elif selected_visualization == "🔥 Análise de Correlação":

    if len(numeric_cols) < 2:

        st.info(
            "São necessárias pelo menos duas colunas numéricas."
        )

    else:

        correlation_columns = numeric_cols[
            :MAX_CORRELATION_COLUMNS
        ]

        corr = chart_df[
            correlation_columns
        ].corr()

        fig = px.imshow(
            corr,
            text_auto=True,
            aspect="auto",
            color_continuous_scale="RdBu",
            title="Matriz de Correlação das Variáveis"
        )

        fig.update_layout(
            height=650,
            margin=dict(l=20, r=20, t=60, b=20)
        )

        st.plotly_chart(
            fig,
            width="stretch",
            key="executive_heatmap"
        )

        if len(numeric_cols) > MAX_CORRELATION_COLUMNS:

            st.caption(
                f"Exibindo as primeiras {MAX_CORRELATION_COLUMNS} "
                "variáveis numéricas por desempenho."
            )


# ==========================================================
# PIE
# ==========================================================

elif selected_visualization == "🥧 Distribuição por Categoria":

    if len(cat_cols) == 0:

        st.info(
            "Não há colunas categóricas disponíveis."
        )

    else:

        category = st.selectbox(
            "Categoria",
            cat_cols,
            key="executive_pie_category"
        )

        counts = (
            chart_df[category]
            .value_counts()
            .head(10)
            .reset_index()
        )

        counts.columns = [
            category,
            "Contagem"
        ]

        fig = px.pie(
            counts,
            names=category,
            values="Contagem",
            hole=0.45,
            title=f"Distribuição de {category}"
        )

        fig.update_layout(
            height=500,
            margin=dict(l=20, r=20, t=60, b=20)
        )

        st.plotly_chart(
            fig,
            width="stretch",
            key="executive_pie"
        )


# ==========================================================
# CATEGORY VS NUMERIC
# ==========================================================

elif selected_visualization == "📊 Categoria vs Numérico":

    if len(cat_cols) == 0 or len(numeric_cols) == 0:

        st.info(
            "São necessárias pelo menos uma coluna categórica e uma numérica."
        )

    else:

        c1, c2 = st.columns(2)

        with c1:

            category = st.selectbox(
                "Categoria",
                cat_cols,
                key="executive_bar_category"
            )

        with c2:

            numeric = st.selectbox(
                "Numérica",
                numeric_cols,
                key="executive_bar_numeric"
            )

        grouped = (
            chart_df
            .groupby(category, dropna=False)[numeric]
            .mean()
            .sort_values(
                ascending=False
            )
            .head(10)
            .reset_index()
        )

        fig = px.bar(
            grouped,
            x=category,
            y=numeric,
            title=f"Média de {numeric} por {category}"
        )

        fig.update_layout(
            height=500,
            margin=dict(l=20, r=20, t=60, b=20)
        )

        st.plotly_chart(
            fig,
            width="stretch",
            key="executive_bar"
        )


# ==========================================================
# OUTLIER
# ==========================================================

elif selected_visualization == "📦 Análise de Outliers":

    if len(cat_cols) == 0 or len(numeric_cols) == 0:

        st.info(
            "São necessárias pelo menos uma coluna categórica e uma numérica."
        )

    else:

        c1, c2 = st.columns(2)

        with c1:

            category = st.selectbox(
                "Categoria",
                cat_cols,
                key="executive_box_category"
            )

        with c2:

            numeric = st.selectbox(
                "Numérica",
                numeric_cols,
                key="executive_box_numeric"
            )

        plot_df = chart_df[
            [category, numeric]
        ].dropna()

        # Prevent extremely high-cardinality boxplots
        top_categories = (
            plot_df[category]
            .value_counts()
            .head(15)
            .index
        )

        plot_df = plot_df[
            plot_df[category].isin(
                top_categories
            )
        ]

        fig = px.box(
            plot_df,
            x=category,
            y=numeric,
            title=f"Análise de Outliers — {numeric}"
        )

        fig.update_layout(
            height=500,
            margin=dict(l=20, r=20, t=60, b=20)
        )

        st.plotly_chart(
            fig,
            width="stretch",
            key="executive_boxplot"
        )


# ==========================================================
# TREND
# ==========================================================

elif selected_visualization == "📈 Análise de Tendência":

    if len(numeric_cols) < 2:

        st.info(
            "São necessárias pelo menos duas colunas numéricas."
        )

    else:

        c1, c2 = st.columns(2)

        with c1:

            x_column = st.selectbox(
                "Eixo X",
                numeric_cols,
                key="executive_line_x"
            )

        with c2:

            y_column = st.selectbox(
                "Eixo Y",
                numeric_cols,
                key="executive_line_y"
            )

        if x_column == y_column:

            st.warning(
                "Selecione duas colunas numéricas diferentes."
            )

        else:

            plot_df = chart_df[
                [x_column, y_column]
            ].dropna()

            plot_df = plot_df.sort_values(
                x_column
            )

            fig = px.line(
                plot_df,
                x=x_column,
                y=y_column,
                title=f"{y_column} vs {x_column}"
            )

            fig.update_layout(
                height=500,
                margin=dict(l=20, r=20, t=60, b=20)
            )

            st.plotly_chart(
                fig,
                width="stretch",
                key="executive_line"
            )


# ==========================================================
# GEOGRAPHIC
# ==========================================================

elif selected_visualization == "🌍 Análise Geográfica":

    location_columns = []

    for col in df.columns:

        name = str(col).lower()

        if any(
            keyword in name
            for keyword in [
                "city",
                "state",
                "country",
                "region",
                "location"
            ]
        ):

            location_columns.append(col)


    if len(location_columns) == 0:

        st.info(
            "Nenhuma coluna geográfica óbvia foi detectada."
        )

    else:

        location = st.selectbox(
            "Localização",
            location_columns,
            key="executive_geo_location"
        )

        geo = (
            chart_df[location]
            .value_counts()
            .head(15)
            .reset_index()
        )

        geo.columns = [
            location,
            "Contagem"
        ]

        fig = px.bar(
            geo,
            x=location,
            y="Contagem",
            title="Principais Localizações do Negócio"
        )

        fig.update_layout(
            height=500,
            margin=dict(l=20, r=20, t=60, b=20)
        )

        st.plotly_chart(
            fig,
            width="stretch",
            key="executive_geo"
        )


# ==========================================================
# AI VISUALIZATION RECOMMENDATIONS
# ==========================================================

st.divider()

st.markdown(
    '<div class="section-label">🤖 Recomendações de Visualização da IA</div>',
    unsafe_allow_html=True
)

if recommendations:

    if isinstance(
        recommendations,
        (list, tuple)
    ):

        for recommendation in recommendations[:5]:

            if isinstance(
                recommendation,
                dict
            ):

                title = recommendation.get(
                    "title",
                    "Análise Recomendada"
                )

                description = recommendation.get(
                    "description",
                    ""
                )

                st.info(
                    f"**{title}** — {description}"
                )

            else:

                st.info(
                    str(recommendation)
                )

    else:

        st.info(
            str(recommendations)
        )

else:

    st.caption(
        "Nenhuma recomendação de visualização adicional foi gerada."
    )


# ==========================================================
# DATASET PREVIEW
# ==========================================================

st.divider()

with st.expander(
    "📋 Ver prévia do dataset"
):

    st.dataframe(
        df.head(20),
        width="stretch",
        height=350
    )


# ==========================================================
# EXECUTIVE RECOMMENDATION
# ==========================================================

st.markdown(
    '<div class="section-label">💼 Central de Ações Executivas</div>',
    unsafe_allow_html=True
)

if score >= 90:

    st.success(
        "✅ A qualidade dos dados é alta. O próximo foco pode "
        "ser modelagem preditiva, previsões e monitoramento "
        "de KPIs."
    )

elif score >= 75:

    st.info(
        "🟡 Os dados são utilizáveis, mas melhorias de "
        "qualidade devem ser concluídas antes de decisões "
        "de IA de alto impacto."
    )

else:

    st.error(
        "🔴 A qualidade dos dados deve ser melhorada antes "
        "de confiar em decisões preditivas ou automatizadas."
    )


# ==========================================================
# AI INSIGHT
# ==========================================================

ai_insight(
    "Executivos devem monitorar a saúde dos dados, os KPIs "
    "do negócio, a atividade dos modelos de IA e das predições, "
    "os padrões do negócio e os riscos emergentes antes de "
    "tomar decisões de alto impacto."
)


# ==========================================================
# NAVIGATION
# ==========================================================

st.divider()

nav_left, nav_right = st.columns(2)

with nav_left:

    if st.button(
        "← Anterior: Copiloto de Negócios IA",
        width="stretch"
    ):

        st.switch_page(
            "pages/3_AI_Business_Copilot.py"
        )


with nav_right:

    if st.button(
        "Próximo: Dashboard Interativo →",
        width="stretch"
    ):

        st.switch_page(
            "pages/5_AutoML.py"
        )


# ==========================================================
# FOOTER
# ==========================================================

page_footer()