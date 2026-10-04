
import streamlit as st
import pandas as pd
import plotly.express as px

from src.database.database import Database
from src.ui.layout import page_header, ai_insight, page_footer


# ----------------------------------------------------
# PAGE CONFIGURATION
# ----------------------------------------------------

st.set_page_config(
    page_title="Histórico de Predições | NexDecision AI",
    page_icon="📜",
    layout="wide"
)

page_header(
    "📜 Histórico de Predições",
    "Acompanhe, analise, filtre e exporte a atividade histórica de predições."
)

st.caption(
    "Monitore execuções de predição, uso de modelos, atividade "
    "de datasets e volume de predições ao longo do tempo."
)

st.markdown("---")


# ----------------------------------------------------
# CUSTOM STYLING
# ----------------------------------------------------

st.markdown(
    """
    <style>
    div[data-testid="stMetric"] {
        background: rgba(128, 128, 128, 0.08);
        border: 1px solid rgba(128, 128, 128, 0.20);
        padding: 18px;
        border-radius: 12px;
    }

    div[data-testid="stMetricLabel"] {
        font-weight: 600;
    }

    .section-description {
        color: #888888;
        font-size: 0.9rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# ----------------------------------------------------
# LOAD PREDICTION HISTORY
# ----------------------------------------------------

@st.cache_data(ttl=30, show_spinner=False)
def load_prediction_history():
    database = Database()
    records = database.get_predictions()

    columns = [
        "ID",
        "Modelo",
        "Arquivo",
        "Linhas",
        "Data da Predição"
    ]

    return pd.DataFrame(records, columns=columns)


try:
    history_df = load_prediction_history()
except Exception as error:
    st.error(f"Não foi possível carregar o histórico de predições: {error}")
    history_df = pd.DataFrame(
        columns=[
            "ID",
            "Modelo",
            "Arquivo",
            "Linhas",
            "Data da Predição"
        ]
    )


# ----------------------------------------------------
# PREPARE DATA
# ----------------------------------------------------

if not history_df.empty:

    history_df["Linhas"] = pd.to_numeric(
        history_df["Linhas"],
        errors="coerce"
    )

    history_df["Data da Predição"] = pd.to_datetime(
        history_df["Data da Predição"],
        errors="coerce"
    )

    history_df["Modelo"] = (
        history_df["Modelo"]
        .fillna("Desconhecido")
        .astype(str)
    )

    history_df["Arquivo"] = (
        history_df["Arquivo"]
        .fillna("Desconhecido")
        .astype(str)
    )


# ----------------------------------------------------
# SIDEBAR FILTERS
# ----------------------------------------------------

st.sidebar.header("🔎 Filtros de Predição")

if not history_df.empty:

    model_options = sorted(
        history_df["Modelo"].unique().tolist()
    )

    file_options = sorted(
        history_df["Arquivo"].unique().tolist()
    )

    selected_models = st.sidebar.multiselect(
        "Filtrar por modelo",
        options=model_options,
        default=model_options
    )

    selected_files = st.sidebar.multiselect(
        "Filtrar por dataset",
        options=file_options,
        default=file_options
    )

    search_text = st.sidebar.text_input(
        "Buscar registros",
        placeholder="Buscar modelo, arquivo ou ID..."
    )

    valid_dates = history_df[
        history_df["Data da Predição"].notna()
    ]["Data da Predição"]

    if not valid_dates.empty:

        min_date = valid_dates.min().date()
        max_date = valid_dates.max().date()

        date_range = st.sidebar.date_input(
            "Período das predições",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )

    else:
        date_range = None

    rows_values = history_df["Linhas"].dropna()

    if not rows_values.empty:

        min_rows = int(rows_values.min())
        max_rows = int(rows_values.max())

        if min_rows < max_rows:
            selected_rows = st.sidebar.slider(
                "Qtd. de linhas do dataset",
                min_value=min_rows,
                max_value=max_rows,
                value=(min_rows, max_rows)
            )
        else:
            selected_rows = (min_rows, max_rows)

    else:
        selected_rows = None

    if st.sidebar.button(
        "🔄 Atualizar histórico de predições",
        use_container_width=True
    ):
        load_prediction_history.clear()
        st.rerun()

    st.sidebar.caption(
        "Os filtros se aplicam aos registros e gráficos desta página."
    )

else:

    selected_models = []
    selected_files = []
    search_text = ""
    date_range = None
    selected_rows = None


# ----------------------------------------------------
# APPLY FILTERS
# ----------------------------------------------------

filtered_df = history_df.copy()

if not history_df.empty:

    filtered_df = filtered_df[
        filtered_df["Modelo"].isin(selected_models)
        & filtered_df["Arquivo"].isin(selected_files)
    ]

    if search_text.strip():

        search = search_text.strip().lower()

        searchable = (
            filtered_df["Modelo"].str.lower().str.contains(
                search, na=False
            )
            | filtered_df["Arquivo"].str.lower().str.contains(
                search, na=False
            )
            | filtered_df["ID"].astype(str).str.contains(
                search, na=False
            )
        )

        filtered_df = filtered_df[searchable]

    if date_range and len(date_range) == 2:

        start_date, end_date = date_range

        prediction_dates = filtered_df["Data da Predição"].dt.date

        filtered_df = filtered_df[
            prediction_dates.isna()
            | (
                (prediction_dates >= start_date)
                & (prediction_dates <= end_date)
            )
        ]

    if selected_rows is not None:

        filtered_df = filtered_df[
            filtered_df["Linhas"].isna()
            | (
                (filtered_df["Linhas"] >= selected_rows[0])
                & (filtered_df["Linhas"] <= selected_rows[1])
            )
        ]


# ----------------------------------------------------
# KPI SUMMARY
# ----------------------------------------------------

st.subheader("📈 Visão Geral das Predições")

k1, k2, k3, k4 = st.columns(4)

total_predictions = len(filtered_df)

models_used = filtered_df["Modelo"].nunique()

datasets_used = filtered_df["Arquivo"].nunique()

total_rows = filtered_df["Linhas"].sum()

with k1:
    st.metric(
        "Total de Predições",
        f"{total_predictions:,}"
    )

with k2:
    st.metric(
        "Modelos Usados",
        f"{models_used:,}"
    )

with k3:
    st.metric(
        "Datasets Usados",
        f"{datasets_used:,}"
    )

with k4:
    st.metric(
        "Total de Linhas Processadas",
        f"{int(total_rows):,}"
        if pd.notna(total_rows)
        else "N/A"
    )

st.caption(
    f"Exibindo {total_predictions:,} de {len(history_df):,} "
    "registros de predição armazenados."
)

st.markdown("---")


# ----------------------------------------------------
# EMPTY STATE
# ----------------------------------------------------

if filtered_df.empty:

    if history_df.empty:
        st.info(
            "Ainda não há histórico de predições. Execute "
            "uma predição na página Estúdio de Predição "
            "primeiro."
        )
    else:
        st.warning(
            "Nenhum registro corresponde aos filtros "
            "selecionados. Ajuste os filtros na "
            "barra lateral."
        )


# ----------------------------------------------------
# PREDICTION RECORDS
# ----------------------------------------------------

else:

    st.subheader("📋 Registros de Predição")

    search_col, sort_col = st.columns([2, 1])

    with search_col:
        st.markdown(
            '<p class="section-description">Revise as execuções '
            'históricas de predição e seus metadados.</p>',
            unsafe_allow_html=True
        )

    with sort_col:
        sort_order = st.selectbox(
            "Ordenar registros",
            [
                "Mais recentes primeiro",
                "Mais antigos primeiro",
                "Maior dataset primeiro",
                "Menor dataset primeiro"
            ]
        )

    display_df = filtered_df.copy()

    if sort_order == "Mais recentes primeiro":
        display_df = display_df.sort_values(
            "Data da Predição",
            ascending=False,
            na_position="last"
        )

    elif sort_order == "Mais antigos primeiro":
        display_df = display_df.sort_values(
            "Data da Predição",
            ascending=True,
            na_position="last"
        )

    elif sort_order == "Maior dataset primeiro":
        display_df = display_df.sort_values(
            "Linhas",
            ascending=False,
            na_position="last"
        )

    else:
        display_df = display_df.sort_values(
            "Linhas",
            ascending=True,
            na_position="last"
        )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        height=350
    )

    csv_data = display_df.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        "📥 Exportar histórico filtrado (CSV)",
        data=csv_data,
        file_name="nexdecision_prediction_history.csv",
        mime="text/csv",
        use_container_width=False
    )

    st.markdown("---")


    # ------------------------------------------------
    # PREDICTION ANALYTICS
    # ------------------------------------------------

    st.subheader("📊 Análise das Predições")

    chart_left, chart_right = st.columns(2)

    model_count = (
        filtered_df["Modelo"]
        .value_counts()
        .rename_axis("Modelo")
        .reset_index(name="Predições")
    )

    with chart_left:

        st.markdown("#### Predições por Modelo")

        model_fig = px.bar(
            model_count,
            x="Modelo",
            y="Predições",
            text="Predições",
            color="Predições",
            color_continuous_scale="Blues"
        )

        model_fig.update_layout(
            xaxis_title="Modelo",
            yaxis_title="Número de Predições",
            showlegend=False,
            margin=dict(l=10, r=10, t=20, b=10)
        )

        model_fig.update_traces(
            textposition="outside"
        )

        st.plotly_chart(
            model_fig,
            use_container_width=True
        )

    with chart_right:

        st.markdown("#### Distribuição de Uso dos Modelos")

        pie_fig = px.pie(
            model_count,
            names="Modelo",
            values="Predições",
            hole=0.48
        )

        pie_fig.update_layout(
            margin=dict(l=10, r=10, t=20, b=10)
        )

        st.plotly_chart(
            pie_fig,
            use_container_width=True
        )


    # ------------------------------------------------
    # DATASET ANALYTICS
    # ------------------------------------------------

    st.markdown("---")

    st.subheader("🗂️ Atividade dos Datasets")

    dataset_count = (
        filtered_df["Arquivo"]
        .value_counts()
        .rename_axis("Dataset")
        .reset_index(name="Predições")
    )

    dataset_left, dataset_right = st.columns(2)

    with dataset_left:

        st.markdown("#### Datasets com Mais Predições")

        dataset_fig = px.bar(
            dataset_count.head(10).sort_values(
                "Predições",
                ascending=True
            ),
            x="Predições",
            y="Dataset",
            orientation="h",
            text="Predições"
        )

        dataset_fig.update_layout(
            xaxis_title="Número de Predições",
            yaxis_title="Dataset",
            margin=dict(l=10, r=10, t=20, b=10)
        )

        st.plotly_chart(
            dataset_fig,
            use_container_width=True
        )

    with dataset_right:

        st.markdown("#### Atividade de Predição ao Longo do Tempo")

        time_df = filtered_df.dropna(
            subset=["Data da Predição"]
        ).copy()

        if not time_df.empty:

            time_df["Data"] = (
                time_df["Data da Predição"].dt.date
            )

            daily_count = (
                time_df.groupby("Data")
                .size()
                .reset_index(name="Predições")
            )

            timeline_fig = px.line(
                daily_count,
                x="Data",
                y="Predições",
                markers=True
            )

            timeline_fig.update_layout(
                xaxis_title="Data",
                yaxis_title="Número de Predições",
                margin=dict(l=10, r=10, t=20, b=10)
            )

            st.plotly_chart(
                timeline_fig,
                use_container_width=True
            )

        else:
            st.info(
                "Não há datas de predição válidas para o gráfico "
                "de linha do tempo."
            )


    # ------------------------------------------------
    # RECORD DETAILS
    # ------------------------------------------------

    st.markdown("---")

    st.subheader("🔍 Inspecionar um Registro de Predição")

    record_ids = filtered_df["ID"].tolist()

    model_names = (
        filtered_df.drop_duplicates("ID")
        .set_index("ID")["Modelo"]
        .to_dict()
    )

    selected_id = st.selectbox(
        "Selecione um registro de predição",
        options=record_ids,
        format_func=lambda record_id: (
            f"{model_names.get(record_id, 'Desconhecido')} "
            f"(ID: {record_id})"
        )
    )

    selected_record = filtered_df[
        filtered_df["ID"] == selected_id
    ].iloc[0]

    d1, d2, d3 = st.columns(3)

    with d1:
        st.markdown("**Modelo**")
        st.write(selected_record["Modelo"])

    with d2:
        st.markdown("**Dataset**")
        st.write(selected_record["Arquivo"])

    with d3:
        st.markdown("**Linhas Processadas**")
        st.write(
            int(selected_record["Linhas"])
            if pd.notna(selected_record["Linhas"])
            else "Desconhecido"
        )

    st.markdown("**Data da Predição**")
    st.write(
        str(selected_record["Data da Predição"])
        if pd.notna(selected_record["Data da Predição"])
        else "Não registrado"
    )

    with st.expander("Ver registro completo"):
        st.json(
            {
                key: (
                    str(value)
                    if pd.notna(value)
                    else None
                )
                for key, value in selected_record.to_dict().items()
            }
        )


# ----------------------------------------------------
# AI INSIGHT
# ----------------------------------------------------

st.markdown("---")

ai_insight(
    "O Histórico de Predições oferece uma trilha de auditoria das "
    "execuções de predição. Use os gráficos de modelos e datasets "
    "para entender os padrões de uso. Este histórico descreve a "
    "atividade registrada; ele não mede, por si só, a acurácia das "
    "predições nem o impacto no negócio."
)


# ----------------------------------------------------
# PAGE NAVIGATION
# ----------------------------------------------------

st.markdown("---")

st.subheader("🧭 Continue Explorando o NexDecision AI")

prev_col, home_col, next_col = st.columns(3)

with prev_col:
    if st.button(
        "⬅️ Histórico de Modelos",
        use_container_width=True
    ):
        st.switch_page("pages/13_Model_History.py")

with home_col:
    if st.button(
        "🏠 Início",
        use_container_width=True
    ):
        st.switch_page("pages/0_Home.py")

with next_col:
    if st.button(
        "➡️ Detecção de Anomalias com IA",
        use_container_width=True
    ):
        st.switch_page("pages/17_AI_Anomaly_Detection.py")


# ----------------------------------------------------
# FOOTER
# ----------------------------------------------------

page_footer()
