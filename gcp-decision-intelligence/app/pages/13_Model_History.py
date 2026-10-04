
import streamlit as st
import pandas as pd

from src.database.database import Database
from src.ui.layout import page_header, ai_insight, page_footer


# ==========================================================
# PAGE CONFIGURATION
# ==========================================================

st.set_page_config(
    page_title="Histórico de Modelos",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ==========================================================
# CUSTOM DESIGN
# ==========================================================

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }

    div.stButton > button,
    div.stDownloadButton > button {
        border-radius: 10px;
        min-height: 42px;
        font-weight: 600;
    }

    [data-testid="stMetric"] {
        padding: 14px;
        border: 1px solid rgba(128, 128, 128, 0.25);
        border-radius: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ==========================================================
# HEADER
# ==========================================================

page_header(
    "🤖 Histórico e Ranking de Modelos",
    "Revise os modelos de machine learning treinados, "
    "compare os scores registrados e explore o histórico "
    "de modelos."
)


# ==========================================================
# LOAD DATABASE
# ==========================================================

try:
    database = Database()
    models = database.get_models()

except Exception as error:
    st.error("Não foi possível carregar o histórico de modelos do banco de dados.")
    st.code(str(error))
    models = None


# ==========================================================
# EMPTY STATE
# ==========================================================

if models is None:
    st.warning("Não foi possível obter o histórico de modelos.")

elif len(models) == 0:

    st.info("🤖 Nenhum modelo de IA foi treinado ainda.")

    st.markdown("### 🚀 Primeiros Passos")
    st.write(
        "Treine um modelo de machine learning com o Motor de "
        "AutoML. Depois que os resultados do treino forem salvos, "
        "eles aparecem aqui para revisão e comparação."
    )

    ai_insight(
        "O Histórico de Modelos registra os resultados de "
        "treino para ajudar você a revisar seus experimentos."
    )

else:

    # ======================================================
    # PREPARE MODEL DATA
    # ======================================================

    model_df = pd.DataFrame(
        models,
        columns=[
            "ID",
            "Dataset",
            "Modelo",
            "Score",
            "Tipo de Problema",
            "Criado em",
        ],
    )

    model_df["Score"] = pd.to_numeric(
        model_df["Score"],
        errors="coerce",
    )

    model_df["Dataset"] = (
        model_df["Dataset"].fillna("Desconhecido").astype(str)
    )

    model_df["Modelo"] = (
        model_df["Modelo"].fillna("Desconhecido").astype(str)
    )

    model_df["Tipo de Problema"] = (
        model_df["Tipo de Problema"].fillna("Desconhecido").astype(str)
    )

    model_df["Criado em"] = (
        model_df["Criado em"].fillna("").astype(str)
    )

    model_df["ID"] = model_df["ID"].astype(str)

    model_df = model_df[
        model_df["Score"].notna()
        & model_df["Score"].map(
            lambda value: pd.notna(value)
            and abs(float(value)) != float("inf")
        )
    ].copy()

    if model_df.empty:

        st.warning(
            "Nenhum modelo com score numérico válido foi encontrado. "
            "Verifique os registros de modelos salvos e seus "
            "scores."
        )

    else:

        # ==================================================
        # SIDEBAR FILTERS
        # ==================================================

        st.sidebar.header("🔎 Filtros de Modelos")

        search = st.sidebar.text_input(
            "Buscar nome do modelo",
            placeholder="ex.: Random Forest",
        )

        available_datasets = sorted(
            model_df["Dataset"].unique().tolist()
        )

        selected_datasets = st.sidebar.multiselect(
            "Datasets",
            options=available_datasets,
            default=available_datasets,
        )

        available_types = sorted(
            model_df["Tipo de Problema"].unique().tolist()
        )

        selected_types = st.sidebar.multiselect(
            "Tipos de problema",
            options=available_types,
            default=available_types,
        )

        available_models = sorted(
            model_df["Modelo"].unique().tolist()
        )

        selected_models = st.sidebar.multiselect(
            "Algoritmos",
            options=available_models,
            default=available_models,
        )

        min_score = float(model_df["Score"].min())
        max_score = float(model_df["Score"].max())

        if min_score < max_score:
            score_range = st.sidebar.slider(
                "Faixa de score registrada",
                min_value=min_score,
                max_value=max_score,
                value=(min_score, max_score),
            )
        else:
            score_range = (min_score, max_score)
            st.sidebar.caption(
                f"Todos os scores válidos são {min_score:.4f}."
            )

        if st.sidebar.button(
            "🔄 Limpar filtros",
            use_container_width=True,
        ):
            st.rerun()

        # ==================================================
        # APPLY FILTERS
        # ==================================================

        filtered_df = model_df.copy()

        if search.strip():
            filtered_df = filtered_df[
                filtered_df["Modelo"].str.contains(
                    search.strip(),
                    case=False,
                    regex=False,
                    na=False,
                )
            ]

        filtered_df = filtered_df[
            filtered_df["Dataset"].isin(selected_datasets)
            & filtered_df["Tipo de Problema"].isin(selected_types)
            & filtered_df["Modelo"].isin(selected_models)
        ]

        filtered_df = filtered_df[
            filtered_df["Score"].between(
                score_range[0],
                score_range[1],
            )
        ]

        # ==================================================
        # SUMMARY METRICS
        # ==================================================

        st.subheader("📊 Resumo dos Modelos")

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            st.metric(
                "Modelos Registrados",
                f"{len(filtered_df):,}",
            )

        with c2:
            st.metric(
                "Algoritmos Distintos",
                filtered_df["Modelo"].nunique(),
            )

        with c3:
            st.metric(
                "Tipos de Problema",
                filtered_df["Tipo de Problema"].nunique(),
            )

        with c4:
            st.metric(
                "Datasets Usados",
                filtered_df["Dataset"].nunique(),
            )

        st.caption(
            f"Exibindo {len(filtered_df):,} de {len(model_df):,} "
            "registros de modelos com scores válidos."
        )

        st.divider()

        # ==================================================
        # LEADERBOARD
        # ==================================================

        st.subheader("🏆 Ranking de Modelos")

        if filtered_df.empty:

            st.warning(
                "Nenhum modelo corresponde aos filtros "
                "atuais. Ajuste os filtros na barra "
                "lateral."
            )

        else:

            sort_order = st.selectbox(
                "Ordenar ranking",
                [
                    "Maior score primeiro",
                    "Menor score primeiro",
                    "Nome do modelo A–Z",
                    "Nome do dataset A–Z",
                ],
            )

            if sort_order == "Maior score primeiro":
                leaderboard = filtered_df.sort_values(
                    "Score",
                    ascending=False,
                )

            elif sort_order == "Menor score primeiro":
                leaderboard = filtered_df.sort_values(
                    "Score",
                    ascending=True,
                )

            elif sort_order == "Nome do modelo A–Z":
                leaderboard = filtered_df.sort_values(
                    "Modelo",
                    ascending=True,
                )

            else:
                leaderboard = filtered_df.sort_values(
                    "Dataset",
                    ascending=True,
                )

            st.dataframe(
                leaderboard,
                use_container_width=True,
                hide_index=True,
            )

            # ==============================================
            # TOP RECORDED SCORE
            # ==============================================

            st.divider()
            st.subheader("🥇 Maior Score Registrado")

            best_model = filtered_df.loc[
                filtered_df["Score"].idxmax()
            ]

            b1, b2, b3, b4 = st.columns(4)

            with b1:
                st.metric(
                    "Modelo",
                    str(best_model["Modelo"]),
                )

            with b2:
                st.metric(
                    "Score",
                    f"{best_model['Score']:.4f}",
                )

            with b3:
                st.metric(
                    "Dataset",
                    str(best_model["Dataset"]),
                )

            with b4:
                st.metric(
                    "Tipo de Problema",
                    str(best_model["Tipo de Problema"]),
                )

            st.caption(
                "Este é o maior score numérico registrado. Scores "
                "só são comparáveis quando a métrica, o método de "
                "avaliação e o contexto do problema são compatíveis."
            )

            # ==============================================
            # PERFORMANCE CHART
            # ==============================================

            st.divider()
            st.subheader("📈 Scores Registrados dos Modelos")

            chart_data = filtered_df[
                ["Modelo", "Dataset", "Score"]
            ].copy()

            chart_data["Rótulo"] = (
                chart_data["Modelo"]
                + " — "
                + chart_data["Dataset"]
            )

            chart_data = chart_data.sort_values(
                "Score",
                ascending=True,
            )

            st.bar_chart(
                chart_data.set_index("Rótulo")["Score"],
                x_label="Modelo — Dataset",
                y_label="Score registrado",
            )

            # ==============================================
            # AVERAGE SCORE BY ALGORITHM
            # ==============================================

            st.divider()
            st.subheader("📊 Score Médio por Algoritmo")

            algorithm_summary = (
                filtered_df.groupby("Modelo")["Score"]
                .agg(["mean", "count", "min", "max"])
                .reset_index()
            )

            algorithm_summary.columns = [
                "Modelo",
                "Score Médio",
                "Nº de Registros",
                "Score Mínimo",
                "Score Máximo",
            ]

            algorithm_summary = algorithm_summary.sort_values(
                "Score Médio",
                ascending=False,
            )

            st.dataframe(
                algorithm_summary.round(4),
                use_container_width=True,
                hide_index=True,
            )

            st.bar_chart(
                algorithm_summary.set_index("Modelo")[
                    "Score Médio"
                ],
                x_label="Algoritmo",
                y_label="Score médio registrado",
            )

            # ==============================================
            # SCORE DISTRIBUTION
            # ==============================================

            st.divider()
            st.subheader("📉 Distribuição dos Scores")

            st.write(
                "Veja a dispersão dos scores registrados. Esta "
                "visão é descritiva e não garante que os modelos "
                "usaram a mesma métrica de avaliação."
            )

            st.line_chart(
                filtered_df.sort_values("Score")[
                    ["Score"]
                ].reset_index(drop=True),
                x_label="Registro de modelo (ordenado)",
                y_label="Score registrado",
            )

            # ==============================================
            # MODEL DETAILS
            # ==============================================

            st.divider()
            st.subheader("🔍 Inspecionar um Registro de Modelo")

            selected_id = st.selectbox(
                "Escolha um registro de modelo",
                options=filtered_df["ID"].tolist(),
                format_func=lambda record_id: (
                    str(
                        filtered_df.loc[
                            filtered_df["ID"] == record_id, "Modelo"
                        ].iloc[0]
                    )
                    + f" (ID: {record_id})"
                ),
            )

            selected_record = filtered_df[
                filtered_df["ID"] == selected_id
            ].iloc[0]

            d1, d2 = st.columns(2)

            with d1:
                st.markdown("**Informações do modelo**")
                st.write("ID do registro:", selected_record["ID"])
                st.write("Algoritmo:", selected_record["Modelo"])
                st.write("Dataset:", selected_record["Dataset"])

            with d2:
                st.markdown("**Informações da avaliação**")
                st.write(
                    "Tipo de problema:",
                    selected_record["Tipo de Problema"],
                )
                st.write(
                    "Score registrado:",
                    f"{selected_record['Score']:.4f}",
                )
                st.write(
                    "Criado em:",
                    selected_record["Criado em"],
                )

            # ==============================================
            # EXPORT
            # ==============================================

            st.divider()
            st.subheader("📥 Exportar Histórico de Modelos")

            export_data = leaderboard.copy()

            export_col1, export_col2 = st.columns(2)

            with export_col1:
                st.download_button(
                    "📥 Baixar modelos filtrados",
                    data=export_data.to_csv(
                        index=False
                    ).encode("utf-8"),
                    file_name="filtered_model_history.csv",
                    mime="text/csv",
                    use_container_width=True,
                )

            with export_col2:
                st.download_button(
                    "📦 Baixar todos os registros válidos",
                    data=model_df.to_csv(
                        index=False
                    ).encode("utf-8"),
                    file_name="all_model_history.csv",
                    mime="text/csv",
                    use_container_width=True,
                )


# ==========================================================
# AI INSIGHT
# ==========================================================

st.divider()

ai_insight(
    "O Histórico de Modelos ajuda a explorar modelos de machine "
    "learning treinados anteriormente, comparar os scores de "
    "avaliação armazenados e revisar os registros de experimentos. "
    "Confirme que os modelos usam métricas compatíveis antes "
    "de comparar os scores."
)


# ==========================================================
# PREVIOUS / HOME / NEXT NAVIGATION
# ==========================================================

st.divider()

st.subheader("🧭 Navegação")

nav_prev, nav_home, nav_next = st.columns(3)

with nav_prev:
    if st.button(
        "⬅️ Anterior: Histórico de Datasets",
        use_container_width=True,
    ):
        st.switch_page("pages/12_Dataset_History.py")

with nav_home:
    if st.button(
        "🏠 Início",
        use_container_width=True,
    ):
        st.switch_page("pages/0_Home.py")

with nav_next:
    if st.button(
        "Próximo: Histórico de Predições ➡️",
        use_container_width=True,
    ):
        st.switch_page("pages/14_Prediction_History.py")


# ==========================================================
# FOOTER
# ==========================================================

page_footer()
