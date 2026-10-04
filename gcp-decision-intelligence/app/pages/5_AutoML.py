import time

import streamlit as st
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

from src.ui.layout import page_header, ai_insight, page_footer
from src.ui.status import loading, success

from src.automl.automl_engine import AutoMLEngine
from src.database.database import Database
from src.model_recommendation.model_recommender import ModelRecommender
from src.model_export.model_exporter import ModelExporter


# ==========================================================
# PAGE CONFIGURATION
# ==========================================================

st.set_page_config(
    page_title="Motor de AutoML com IA",
    page_icon="🤖",
    layout="wide"
)


# ==========================================================
# PERFORMANCE SETTINGS
# ==========================================================

MAX_TRAINING_ROWS = 15000


# ==========================================================
# CUSTOM CSS
# ==========================================================

st.markdown(
    """
    <style>

    .automl-hero {
        padding: 1.6rem 1.8rem;
        border-radius: 18px;
        background: linear-gradient(
            135deg,
            rgba(30, 64, 175, 0.12),
            rgba(14, 116, 144, 0.10)
        );
        border: 1px solid rgba(100, 116, 139, 0.18);
        margin-bottom: 1.2rem;
    }

    .automl-title {
        font-size: 2rem;
        font-weight: 800;
        margin-bottom: 0.35rem;
    }

    .automl-subtitle {
        color: #64748b;
        font-size: 1rem;
    }

    .config-card {
        padding: 1rem 1.2rem;
        border-radius: 15px;
        background: #eef6ff;
        border: 1px solid rgba(59, 130, 246, 0.18);
        min-height: 105px;
    }

    .config-title {
        font-weight: 750;
        font-size: 0.9rem;
    }

    .config-value {
        font-size: 1.2rem;
        font-weight: 800;
        margin-top: 0.25rem;
    }

    .decision-card {
        padding: 1.3rem;
        border-radius: 16px;
        background: #172554;
        color: white;
        border: 1px solid #1e3a5f;
    }

    .decision-title {
        font-size: 1rem;
        font-weight: 800;
    }

    .decision-value {
        font-size: 1.45rem;
        font-weight: 850;
        margin-top: 0.35rem;
    }

    .performance-note {
        padding: 0.85rem 1rem;
        border-radius: 12px;
        background: rgba(14, 116, 144, 0.08);
        border: 1px solid rgba(14, 116, 144, 0.15);
        color: #475569;
        font-size: 0.9rem;
    }

    .section-label {
        font-size: 1.35rem;
        font-weight: 800;
        margin-top: 1rem;
        margin-bottom: 0.6rem;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ==========================================================
# HEADER
# ==========================================================

page_header(
    "🤖 Motor de AutoML com IA",
    "Treine, compare e recomende automaticamente o melhor modelo de Machine Learning."
)

st.markdown(
    """
    <div class="automl-hero">
        <div class="automl-title">
            🧠 Central de Decisão de Machine Learning Automatizado
        </div>
        <div class="automl-subtitle">
            Prepare seu dataset, identifique o alvo da predição,
            compare algoritmos de machine learning e exporte o
            modelo de melhor desempenho.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# ==========================================================
# DATASET CHECK
# ==========================================================

if "dataset" not in st.session_state:

    st.warning(
        "⚠️ Envie um dataset primeiro."
    )

    st.stop()


df = st.session_state["dataset"]

filename = st.session_state.get(
    "filename",
    "Dataset enviado"
)


if df is None or df.empty:

    st.error(
        "O dataset enviado está vazio."
    )

    st.stop()


st.success(
    f"✅ Dataset carregado: **{filename}**"
)


# ==========================================================
# DATASET INFORMATION
# ==========================================================

rows = len(df)
columns = len(df.columns)

missing = int(
    df.isnull().sum().sum()
)

duplicates = int(
    df.duplicated().sum()
)

numeric_count = len(
    df.select_dtypes(include="number").columns
)

categorical_count = len(
    df.select_dtypes(exclude="number").columns
)


# ==========================================================
# DATASET STATUS
# ==========================================================

st.markdown(
    '<div class="section-label">📊 Prontidão do Dataset</div>',
    unsafe_allow_html=True
)

c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    st.metric(
        "Linhas",
        f"{rows:,}"
    )

with c2:
    st.metric(
        "Colunas",
        columns
    )

with c3:
    st.metric(
        "Ausentes",
        f"{missing:,}"
    )

with c4:
    st.metric(
        "Numéricas",
        numeric_count
    )

with c5:
    st.metric(
        "Categóricas",
        categorical_count
    )


st.divider()


# ==========================================================
# TARGET DETECTION
# ==========================================================

ignore_columns = [
    "order_id",
    "customer_id",
    "product_id",
    "seller_id",
    "row id",
    "row_id",
    "id"
]


candidate_columns = [
    c
    for c in df.columns
    if str(c).lower().strip()
    not in ignore_columns
]


if len(candidate_columns) == 0:

    st.error(
        "Nenhuma coluna-alvo adequada foi detectada."
    )

    st.stop()


# ==========================================================
# TARGET SELECTION
# ==========================================================

st.markdown(
    '<div class="section-label">🎯 Configuração da Predição</div>',
    unsafe_allow_html=True
)

target = st.selectbox(
    "Alvo da Predição",
    candidate_columns,
    help="Selecione a coluna que o motor de AutoML deve prever."
)


# ==========================================================
# TARGET PROFILE
# ==========================================================

target_series = df[target]

target_unique = target_series.nunique(
    dropna=True
)

target_missing = int(
    target_series.isnull().sum()
)

target_type = str(
    target_series.dtype
)


if pd.api.types.is_numeric_dtype(
    target_series
):

    if target_unique <= 10:

        suggested_problem = "Classificação"

    else:

        suggested_problem = "Regressão"

else:

    suggested_problem = "Classificação"


p1, p2, p3, p4 = st.columns(4)

with p1:

    st.metric(
        "Alvo",
        target
    )

with p2:

    st.metric(
        "Valores Únicos",
        f"{target_unique:,}"
    )

with p3:

    st.metric(
        "Alvo Ausente",
        f"{target_missing:,}"
    )

with p4:

    st.metric(
        "Tipo Sugerido",
        suggested_problem
    )


# ==========================================================
# LARGE DATASET NOTICE
# ==========================================================

if rows > MAX_TRAINING_ROWS:

    st.info(
        f"""
        ⚡ **Dataset grande detectado**

        O dataset enviado tem **{rows:,} linhas**.

        O AutoML usará no máximo
        **{MAX_TRAINING_ROWS:,} linhas** no treino
        para manter a comparação de modelos ágil.

        Seu dataset original não será alterado.
        """
    )


# ==========================================================
# TRAINING PREPROCESSOR
# ==========================================================

@st.cache_data(
    show_spinner=False
)
def prepare_training_data(
    dataframe,
    target_column,
    max_rows
):

    data = dataframe.copy()

    # ------------------------------------------------------
    # Remove missing rows
    # ------------------------------------------------------

    data = (
        data
        .dropna()
        .reset_index(drop=True)
    )

    # ------------------------------------------------------
    # Large dataset sampling
    # ------------------------------------------------------

    sampled = False

    if len(data) > max_rows:

        data = data.sample(
            max_rows,
            random_state=42
        ).reset_index(
            drop=True
        )

        sampled = True

    # ------------------------------------------------------
    # Remove constant columns
    # ------------------------------------------------------

    constant_columns = [
        c
        for c in data.columns
        if data[c].nunique() <= 1
    ]

    data = data.drop(
        columns=constant_columns,
        errors="ignore"
    )

    if target_column not in data.columns:

        raise ValueError(
            "A coluna-alvo foi removida durante o pré-processamento."
        )

    # ------------------------------------------------------
    # Encode features
    # ------------------------------------------------------

    feature_encoders = {}

    for col in data.columns:

        if col == target_column:
            continue

        # ----------------------------------------------
        # Date conversion
        # ----------------------------------------------

        if (
            pd.api.types.is_datetime64_any_dtype(
                data[col]
            )
        ):

            data[col] = (
                data[col]
                .astype("int64")
                // 10**9
            )

            continue

        # ----------------------------------------------
        # Try date detection
        # ----------------------------------------------

        if not pd.api.types.is_numeric_dtype(
            data[col]
        ):

            converted = pd.to_datetime(
                data[col],
                errors="coerce"
            )

            if (
                converted.notna().mean()
                >= 0.8
            ):

                data[col] = (
                    converted
                    .astype("int64")
                    // 10**9
                )

                continue

        # ----------------------------------------------
        # Categorical encoding
        # ----------------------------------------------

        if not pd.api.types.is_numeric_dtype(
            data[col]
        ):

            encoder = LabelEncoder()

            data[col] = encoder.fit_transform(
                data[col].astype(str)
            )

            feature_encoders[col] = encoder

    # ------------------------------------------------------
    # Target encoding
    # ------------------------------------------------------

    target_encoder = None

    if not pd.api.types.is_numeric_dtype(
        data[target_column]
    ):

        target_encoder = LabelEncoder()

        data[target_column] = (
            target_encoder
            .fit_transform(
                data[target_column]
                .astype(str)
            )
        )

    # ------------------------------------------------------
    # Split
    # ------------------------------------------------------

    X = data.drop(
        columns=[target_column]
    )

    y = data[target_column]

    if X.shape[1] == 0:

        raise ValueError(
            "Não restaram colunas de variáveis utilizáveis após o pré-processamento."
        )

    X_train, X_test, y_train, y_test = (
        train_test_split(
            X,
            y,
            test_size=0.20,
            random_state=42
        )
    )

    return (
        X_train,
        X_test,
        y_train,
        y_test,
        feature_encoders,
        target_encoder,
        sampled,
        constant_columns
    )


# ==========================================================
# TRAINING SESSION STATE
# ==========================================================

if "automl_result" not in st.session_state:

    st.session_state["automl_result"] = None


# ==========================================================
# TRAIN BUTTON
# ==========================================================

st.markdown(
    '<div class="section-label">🚀 Treino dos Modelos</div>',
    unsafe_allow_html=True
)

train_button = st.button(
    "🚀 Treinar e Comparar Modelos de IA",
    type="primary",
    width="stretch"
)


# ==========================================================
# TRAINING
# ==========================================================

if train_button:

    start_time = time.perf_counter()

    try:

        with st.spinner(
            "⚙️ Preparando os dados de treino..."
        ):

            (
                X_train,
                X_test,
                y_train,
                y_test,
                feature_encoders,
                target_encoder,
                sampled,
                constant_columns
            ) = prepare_training_data(
                df,
                target,
                MAX_TRAINING_ROWS
            )


        status = st.empty()

        progress = st.progress(
            10
        )

        status.info(
            "🔄 Preparando o pipeline de treino de IA..."
        )


        # --------------------------------------------------
        # AUTOML
        # --------------------------------------------------

        automl = AutoMLEngine()

        progress.progress(
            25
        )

        status.info(
            "🤖 Comparando algoritmos de machine learning..."
        )


        with loading(
            "Treinando e avaliando modelos..."
        ):

            results = automl.compare_models(
                X_train,
                X_test,
                y_train,
                y_test
            )


        progress.progress(
            75
        )

        status.info(
            "📊 Avaliando o desempenho dos modelos..."
        )


        if not results:

            raise ValueError(
                "O AutoML não retornou resultados de modelos."
            )


        best_model = max(
            results,
            key=results.get
        )

        progress.progress(
            90
        )

        status.info(
            "🏆 Selecionando o modelo de melhor desempenho..."
        )


        # --------------------------------------------------
        # EXPORT
        # --------------------------------------------------

        exporter = ModelExporter()

        filepath = exporter.export(
            model=automl.best_model,
            model_name=best_model.replace(
                " ",
                "_"
            ),
            feature_names=list(
                X_train.columns
            ),
            target_column=target,
            problem_type=automl.problem_type
        )


        # --------------------------------------------------
        # SAVE DATABASE HISTORY
        # --------------------------------------------------

        database = Database()

        database.save_model(
            filename,
            best_model,
            results[best_model],
            automl.problem_type
        )


        # --------------------------------------------------
        # TRAINING TIME
        # --------------------------------------------------

        elapsed_time = (
            time.perf_counter()
            - start_time
        )


        # --------------------------------------------------
        # FEATURE IMPORTANCE
        # --------------------------------------------------

        importance = None

        try:

            importance = automl.feature_importance(
                X_train.columns
            )

        except Exception:

            importance = None


        # --------------------------------------------------
        # RECOMMENDATIONS
        # --------------------------------------------------

        recommender = ModelRecommender()

        recommendations = recommender.recommend(
            best_model,
            results[best_model],
            automl.problem_type
        )


        # --------------------------------------------------
        # STORE RESULT
        # --------------------------------------------------

        st.session_state[
            "automl_result"
        ] = {

            "results": results,

            "best_model": best_model,

            "problem_type":
                automl.problem_type,

            "feature_names":
                list(X_train.columns),

            "importance":
                importance,

            "recommendations":
                recommendations,

            "training_time":
                elapsed_time,

            "training_rows":
                len(X_train) + len(X_test),

            "sampled":
                sampled,

            "constant_columns":
                constant_columns,

            "target":
                target,

            "filepath":
                filepath,

            "score":
                results[best_model]
        }


        progress.progress(
            100
        )

        status.success(
            "✅ AutoML concluído com sucesso!"
        )

        st.toast(
            "🎉 Treino dos modelos concluído!"
        )


    except Exception as e:

        st.error(
            f"❌ Falha no treino do AutoML: {e}"
        )


# ==========================================================
# SHOW TRAINING RESULT
# ==========================================================

result = st.session_state.get(
    "automl_result"
)


if result is None:

    st.info(
        "👆 Selecione um alvo de predição e clique "
        "em **Treinar e Comparar Modelos de IA** para "
        "iniciar o AutoML."
    )

    st.markdown(
        """
        <div class="performance-note">
            ⚡ <b>Otimização de desempenho:</b>
            o pré-processamento fica em cache e os modelos são treinados
            somente depois que você clica no botão de treino.
            As reexecuções da interface do Streamlit não
            retreinam seus modelos automaticamente.
        </div>
        """,
        unsafe_allow_html=True
    )

else:

    results = result["results"]

    best_model = result["best_model"]

    problem_type = result["problem_type"]

    importance = result["importance"]

    recommendations = result["recommendations"]

    training_time = result["training_time"]

    training_rows = result["training_rows"]

    sampled = result["sampled"]

    constant_columns = result[
        "constant_columns"
    ]

    target_used = result["target"]

    filepath = result["filepath"]

    best_score = result["score"]


    # ======================================================
    # SUCCESS
    # ======================================================

    st.success(
        f"🏆 Melhor modelo selecionado: **{best_model}**"
    )


    # ======================================================
    # DECISION SUMMARY
    # ======================================================

    st.markdown(
        '<div class="section-label">🏆 Decisão de Modelo da IA</div>',
        unsafe_allow_html=True
    )

    d1, d2, d3, d4 = st.columns(4)

    with d1:

        st.markdown(
            f"""
            <div class="decision-card">
                <div class="decision-title">
                    🥇 Melhor Modelo
                </div>
                <div class="decision-value">
                    {best_model}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


    with d2:

        st.markdown(
            f"""
            <div class="decision-card">
                <div class="decision-title">
                    🎯 Tipo de Problema
                </div>
                <div class="decision-value">
                    {problem_type.title()}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


    with d3:

        score_display = (
            f"{best_score:.2f}"
        )

        st.markdown(
            f"""
            <div class="decision-card">
                <div class="decision-title">
                    📈 Score do Modelo
                </div>
                <div class="decision-value">
                    {score_display}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


    with d4:

        st.markdown(
            f"""
            <div class="decision-card">
                <div class="decision-title">
                    ⏱ Tempo de Treino
                </div>
                <div class="decision-value">
                    {training_time:.1f}s
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


    # ======================================================
    # TRAINING DETAILS
    # ======================================================

    st.markdown(
        '<div class="section-label">⚙️ Configuração do Treino</div>',
        unsafe_allow_html=True
    )

    t1, t2, t3, t4 = st.columns(4)

    with t1:

        st.metric(
            "Alvo",
            target_used
        )

    with t2:

        st.metric(
            "Linhas de Treino",
            f"{training_rows:,}"
        )

    with t3:

        st.metric(
            "Modelos Comparados",
            len(results)
        )

    with t4:

        st.metric(
            "Variáveis Usadas",
            len(result["feature_names"])
        )


    if sampled:

        st.info(
            f"⚡ O treino usou no máximo {MAX_TRAINING_ROWS:,} "
            "linhas amostradas porque o dataset "
            "original era maior."
        )


    if constant_columns:

        with st.expander(
            "🔍 Detalhes do Pré-processamento"
        ):

            st.write(
                "Colunas constantes removidas:"
            )

            st.write(
                constant_columns
            )


    # ======================================================
    # MODEL COMPARISON
    # ======================================================

    st.markdown(
        '<div class="section-label">📊 Comparação de Modelos</div>',
        unsafe_allow_html=True
    )

    results_df = pd.DataFrame(
        {
            "Modelo": list(
                results.keys()
            ),

            "Score": list(
                results.values()
            )
        }
    )


    results_df = results_df.sort_values(
        "Score",
        ascending=False
    ).reset_index(
        drop=True
    )


    results_df.insert(
        0,
        "Posição",
        range(
            1,
            len(results_df) + 1
        )
    )


    st.dataframe(
        results_df,
        width="stretch",
        hide_index=True
    )


    # ======================================================
    # MODEL COMPARISON CHART
    # ======================================================

    st.bar_chart(
        results_df.set_index(
            "Modelo"
        )["Score"]
    )


    # ======================================================
    # MODEL PERFORMANCE
    # ======================================================

    if problem_type == "classification":

        st.caption(
            "O score de classificação é exibido com "
            "a métrica retornada pelo motor de AutoML."
        )

    else:

        st.caption(
            "O score de regressão é exibido com "
            "a métrica retornada pelo motor de AutoML."
        )


    st.divider()


    # ======================================================
    # FEATURE IMPORTANCE
    # ======================================================

    st.markdown(
        '<div class="section-label">📌 Importância das Variáveis</div>',
        unsafe_allow_html=True
    )


    if importance is not None:

        imp_df = pd.DataFrame(
            {
                "Variável":
                    list(
                        importance.keys()
                    ),

                "Importância":
                    list(
                        importance.values()
                    )
            }
        )


        imp_df = imp_df.sort_values(
            "Importância",
            ascending=False
        )


        top_features = imp_df.head(
            15
        )


        st.dataframe(
            top_features,
            width="stretch",
            hide_index=True
        )


        st.bar_chart(
            top_features.set_index(
                "Variável"
            )["Importância"]
        )


    else:

        st.info(
            "A importância das variáveis não "
            "está disponível para o modelo selecionado."
        )


    # ======================================================
    # AI RECOMMENDATIONS
    # ======================================================

    st.markdown(
        '<div class="section-label">🤖 Recomendações de Modelo da IA</div>',
        unsafe_allow_html=True
    )


    if recommendations:

        for recommendation in recommendations:

            st.success(
                str(
                    recommendation
                )
            )

    else:

        st.info(
            "Nenhuma recomendação adicional foi gerada."
        )


    # ======================================================
    # EXPORT STATUS
    # ======================================================

    st.markdown(
        '<div class="section-label">💾 Exportação do Modelo</div>',
        unsafe_allow_html=True
    )


    st.success(
        "✅ Melhor modelo exportado com sucesso."
    )
    st.balloons()


    st.caption(
        f"Caminho do modelo salvo: {filepath}"
    )


    # ======================================================
    # AI INSIGHT
    # ======================================================

    ai_insight(
        "O motor de AutoML comparou vários algoritmos de machine "
        "learning e selecionou o modelo de melhor desempenho. "
        "Antes de colocar em produção, revise o desempenho, "
        "a importância das variáveis e a relevância para o "
        "negócio."
    )


# ==========================================================
# NAVIGATION
# ==========================================================

st.divider()

nav_left, nav_right = st.columns(2)


with nav_left:

    if st.button(
        "← Anterior: Copiloto",
        width="stretch"
    ):

        st.switch_page(
            "pages/3_AI_Business_Copilot.py"
        )


with nav_right:

    if st.button(
        "Próximo: Previsões →",
        width="stretch"
    ):

        st.switch_page(
            "pages/6_Business_Forecasting.py"
        )


# ==========================================================
# FOOTER
# ==========================================================

page_footer()