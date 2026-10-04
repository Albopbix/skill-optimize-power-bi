
import streamlit as st
import pandas as pd

from src.database.database import Database
from src.ui.layout import page_header, ai_insight, page_footer


# ==========================================================
# PAGE CONFIGURATION
# ==========================================================

st.set_page_config(
    page_title="Histórico de Datasets",
    page_icon="📂",
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

    div.stButton > button {
        border-radius: 10px;
        min-height: 42px;
        font-weight: 600;
    }

    div.stDownloadButton > button {
        border-radius: 10px;
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
# PAGE HEADER
# ==========================================================

page_header(
    "📂 Histórico de Datasets",
    "Acompanhe os datasets enviados, consulte registros "
    "históricos, analise padrões de envio e exporte o "
    "histórico."
)


# ==========================================================
# LOAD DATABASE
# ==========================================================

try:
    database = Database()
    history = database.get_uploads()

except Exception as error:
    st.error("Não foi possível carregar o histórico de datasets do banco de dados.")
    st.code(str(error))
    history = None


# ==========================================================
# EMPTY STATE
# ==========================================================

if history is None:
    st.warning("Não foi possível obter o histórico de datasets.")

elif len(history) == 0:
    st.info(
        "📂 Nenhum dataset foi enviado ainda. Envie um "
        "dataset para começar seu histórico."
    )

    st.markdown("### 🚀 Primeiros Passos")
    st.write(
        "Depois de enviar um dataset CSV ou Excel, as informações "
        "do envio aparecem aqui para acompanhamento e revisão."
    )

else:

    # ======================================================
    # CREATE DATAFRAME
    # ======================================================

    history_df = pd.DataFrame(
        history,
        columns=[
            "ID",
            "Arquivo",
            "Linhas",
            "Colunas",
            "Tipo de Dataset",
            "Data do Envio",
        ],
    )

    history_df["Linhas"] = pd.to_numeric(
        history_df["Linhas"], errors="coerce"
    ).fillna(0)

    history_df["Colunas"] = pd.to_numeric(
        history_df["Colunas"], errors="coerce"
    ).fillna(0)

    history_df["Arquivo"] = (
        history_df["Arquivo"].fillna("Desconhecido").astype(str)
    )

    history_df["Tipo de Dataset"] = (
        history_df["Tipo de Dataset"].fillna("Desconhecido").astype(str)
    )

    history_df["Data do Envio"] = (
        history_df["Data do Envio"].fillna("").astype(str)
    )

    # Keep the original display value and create a parsed date
    # for filtering and chronological sorting.
    history_df["_parsed_date"] = pd.to_datetime(
        history_df["Data do Envio"],
        errors="coerce",
        utc=True,
    )

    history_df["_parsed_date"] = (
        history_df["_parsed_date"].dt.tz_convert(None)
    )

    history_df["_filename_lower"] = (
        history_df["Arquivo"].str.lower()
    )

    # ======================================================
    # SIDEBAR FILTERS
    # ======================================================

    st.sidebar.header("🔎 Filtros do Histórico")

    search = st.sidebar.text_input(
        "Buscar arquivo",
        placeholder="Digite o nome de um arquivo...",
    )

    available_types = sorted(
        history_df["Tipo de Dataset"].unique().tolist()
    )

    selected_types = st.sidebar.multiselect(
        "Tipo de dataset",
        options=available_types,
        default=available_types,
    )

    min_rows = int(history_df["Linhas"].min())
    max_rows = int(history_df["Linhas"].max())

    row_range = st.sidebar.slider(
        "Número de linhas",
        min_value=min_rows,
        max_value=max_rows,
        value=(min_rows, max_rows),
    )

    valid_dates = history_df["_parsed_date"].dropna()

    date_range = None

    if not valid_dates.empty:

        first_date = valid_dates.min().date()
        last_date = valid_dates.max().date()

        date_range = st.sidebar.date_input(
            "Período de envio",
            value=(first_date, last_date),
        )

    if st.sidebar.button(
        "🔄 Limpar filtros",
        use_container_width=True,
    ):
        st.rerun()

    # ======================================================
    # APPLY FILTERS
    # ======================================================

    filtered_df = history_df.copy()

    if search.strip():
        filtered_df = filtered_df[
            filtered_df["_filename_lower"].str.contains(
                search.strip().lower(),
                regex=False,
                na=False,
            )
        ]

    filtered_df = filtered_df[
        filtered_df["Tipo de Dataset"].isin(selected_types)
    ]

    filtered_df = filtered_df[
        filtered_df["Linhas"].between(
            row_range[0], row_range[1]
        )
    ]

    if date_range and len(date_range) == 2:

        start_date, end_date = date_range

        start_timestamp = pd.Timestamp(start_date)
        end_timestamp = (
            pd.Timestamp(end_date) + pd.Timedelta(days=1)
        )

        # Retain records with unparseable dates rather than
        # silently removing them from the history.
        in_date_range = (
            filtered_df["_parsed_date"].isna()
            | (
                (filtered_df["_parsed_date"] >= start_timestamp)
                & (filtered_df["_parsed_date"] < end_timestamp)
            )
        )

        filtered_df = filtered_df[in_date_range]

    # ======================================================
    # PAGE TITLE AND SUMMARY
    # ======================================================

    st.subheader("📊 Resumo dos Envios")

    total_datasets = len(history_df)
    filtered_datasets = len(filtered_df)

    total_rows = int(filtered_df["Linhas"].sum())
    total_columns = int(filtered_df["Colunas"].sum())

    dataset_types_count = filtered_df["Tipo de Dataset"].nunique()

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric(
            "📁 Total de Envios",
            f"{filtered_datasets:,}",
            delta=f"{filtered_datasets - total_datasets:+,} vs total"
            if filtered_datasets != total_datasets else None,
        )

    with c2:
        st.metric("📄 Linhas Somadas", f"{total_rows:,}")

    with c3:
        st.metric("📊 Colunas Somadas", f"{total_columns:,}")

    with c4:
        st.metric("🗂️ Tipos de Dataset", dataset_types_count)

    st.caption(
        f"Exibindo {filtered_datasets:,} de "
        f"{total_datasets:,} envios históricos."
    )

    st.divider()

    # ======================================================
    # HISTORY TABLE
    # ======================================================

    st.subheader("📋 Registros de Envio")

    sort_by = st.selectbox(
        "Ordenar registros por",
        [
            "Envio mais recente",
            "Envio mais antigo",
            "Arquivo A–Z",
            "Mais linhas",
            "Mais colunas",
        ],
    )

    if sort_by == "Envio mais recente":
        filtered_df = filtered_df.sort_values(
            "_parsed_date",
            ascending=False,
            na_position="last",
        )

    elif sort_by == "Envio mais antigo":
        filtered_df = filtered_df.sort_values(
            "_parsed_date",
            ascending=True,
            na_position="last",
        )

    elif sort_by == "Arquivo A–Z":
        filtered_df = filtered_df.sort_values(
            "Arquivo",
            ascending=True,
        )

    elif sort_by == "Mais linhas":
        filtered_df = filtered_df.sort_values(
            "Linhas",
            ascending=False,
        )

    elif sort_by == "Mais colunas":
        filtered_df = filtered_df.sort_values(
            "Colunas",
            ascending=False,
        )

    display_df = filtered_df[
        [
            "ID",
            "Arquivo",
            "Linhas",
            "Colunas",
            "Tipo de Dataset",
            "Data do Envio",
        ]
    ].copy()

    if display_df.empty:
        st.warning(
            "Nenhum registro de envio corresponde aos "
            "filtros atuais. Tente alterar a busca ou "
            "os filtros."
        )

    else:
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
        )

    # ======================================================
    # DATASET DETAIL VIEW
    # ======================================================

    st.divider()
    st.subheader("🔍 Inspecionar um Envio")

    if not filtered_df.empty:

        selected_index = st.selectbox(
            "Escolha um envio",
            options=filtered_df.index.tolist(),
            format_func=lambda idx: (
                f"{filtered_df.loc[idx, 'Arquivo']} "
                f"(ID: {filtered_df.loc[idx, 'ID']})"
            ),
        )

        selected_record = filtered_df.loc[selected_index]

        d1, d2, d3 = st.columns(3)

        with d1:
            st.metric(
                "Linhas",
                f"{int(selected_record['Linhas']):,}",
            )

        with d2:
            st.metric(
                "Colunas",
                f"{int(selected_record['Colunas']):,}",
            )

        with d3:
            st.metric(
                "Tipo de Dataset",
                str(selected_record["Tipo de Dataset"]),
            )

        st.write("**Arquivo:**", selected_record["Arquivo"])
        st.write("**ID do envio:**", selected_record["ID"])
        st.write("**Data do envio:**", selected_record["Data do Envio"])

        st.caption(
            "Esta visão mostra os metadados de envio armazenados. "
            "Ela não recarrega o dataset original automaticamente."
        )

    # ======================================================
    # DATASET TYPE DISTRIBUTION
    # ======================================================

    st.divider()
    st.subheader("📈 Distribuição por Tipo de Dataset")

    if not filtered_df.empty:

        dataset_count = (
            filtered_df["Tipo de Dataset"]
            .value_counts()
            .rename_axis("Tipo de Dataset")
            .reset_index(name="Contagem")
        )

        chart_col, summary_col = st.columns([2, 1])

        with chart_col:
            st.bar_chart(
                dataset_count.set_index("Tipo de Dataset"),
                x_label="Tipo de Dataset",
                y_label="Número de Envios",
            )

        with summary_col:
            st.markdown("**Detalhamento dos envios**")

            st.dataframe(
                dataset_count,
                use_container_width=True,
                hide_index=True,
            )

    else:
        st.info("Não há dados disponíveis para o gráfico de distribuição.")

    # ======================================================
    # ROW COUNT DISTRIBUTION
    # ======================================================

    st.divider()
    st.subheader("📊 Visão Geral do Tamanho dos Datasets")

    if not filtered_df.empty:

        size_col1, size_col2 = st.columns(2)

        with size_col1:
            st.metric(
                "Média de Linhas por Envio",
                f"{filtered_df['Linhas'].mean():,.1f}",
            )

        with size_col2:
            st.metric(
                "Maior Dataset",
                f"{int(filtered_df['Linhas'].max()):,} linhas",
            )

        size_distribution = filtered_df[
            ["Arquivo", "Linhas"]
        ].copy()

        size_distribution = size_distribution.sort_values(
            "Linhas",
            ascending=False,
        ).head(15)

        st.bar_chart(
            size_distribution.set_index("Arquivo"),
            x_label="Arquivo",
            y_label="Linhas",
        )

    # ======================================================
    # DOWNLOAD HISTORY
    # ======================================================

    st.divider()
    st.subheader("📥 Exportar Histórico")

    download_col1, download_col2 = st.columns(2)

    with download_col1:

        export_filtered = filtered_df[
            [
                "ID",
                "Arquivo",
                "Linhas",
                "Colunas",
                "Tipo de Dataset",
                "Data do Envio",
            ]
        ]

        st.download_button(
            "📥 Baixar registros filtrados",
            data=export_filtered.to_csv(
                index=False
            ).encode("utf-8"),
            file_name="filtered_dataset_history.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with download_col2:

        export_all = history_df[
            [
                "ID",
                "Arquivo",
                "Linhas",
                "Colunas",
                "Tipo de Dataset",
                "Data do Envio",
            ]
        ]

        st.download_button(
            "📦 Baixar todos os registros",
            data=export_all.to_csv(
                index=False
            ).encode("utf-8"),
            file_name="all_dataset_history.csv",
            mime="text/csv",
            use_container_width=True,
        )


# ==========================================================
# AI INSIGHT
# ==========================================================

st.divider()

ai_insight(
    "O Histórico de Datasets oferece um registro pesquisável dos "
    "datasets enviados. Filtros, resumos de tamanho e registros "
    "para download ajudam a acompanhar seus ativos de dados e "
    "manter a rastreabilidade do projeto."
)


# ==========================================================
# PREVIOUS / HOME / NEXT PAGE NAVIGATION
# ==========================================================

st.divider()

st.subheader("🧭 Navegação")

st.caption(
    "Navegue entre a página anterior, o Início e a próxima "
    "página do NexDecision AI."
)

nav_prev, nav_home, nav_next = st.columns(3)

with nav_prev:

    if st.button(
        "⬅️ Anterior: Chat com IA",
        use_container_width=True,
    ):
        st.switch_page("pages/11_AI_Chat.py")

with nav_home:

    if st.button(
        "🏠 Início",
        use_container_width=True,
    ):
        st.switch_page("pages/0_Home.py")

with nav_next:

    if st.button(
        "Próximo: Histórico de Modelos ➡️",
        use_container_width=True,
    ):
        st.switch_page("pages/13_Model_History.py")


# ==========================================================
# FOOTER
# ==========================================================

page_footer()
