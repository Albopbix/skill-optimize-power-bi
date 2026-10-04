
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

from src.ui.layout import page_header, ai_insight, page_footer


# ==========================================================
# PAGE CONFIGURATION
# ==========================================================

st.set_page_config(
    page_title="Dashboard Interativo",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ==========================================================
# CUSTOM STYLING
# ==========================================================

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }

    div[data-testid="stMetric"] {
        background: var(--secondary-background-color);
        border: 1px solid rgba(128,128,128,0.20);
        padding: 16px;
        border-radius: 12px;
    }

    div[data-testid="stPlotlyChart"] {
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
    "📊 Dashboard Interativo",
    "Explore os dados do negócio com visualizações interativas, "
    "descubra padrões e investigue a qualidade dos dados."
)


# ==========================================================
# DATASET VALIDATION
# ==========================================================

if "dataset" not in st.session_state:
    st.warning("Envie um dataset primeiro.")
    st.stop()

original_df = st.session_state["dataset"]

if not isinstance(original_df, pd.DataFrame):
    st.error("O dataset enviado não é um DataFrame válido.")
    st.stop()

if original_df.empty:
    st.warning("O dataset enviado está vazio.")
    st.stop()

# Preserve the original uploaded data.
df = original_df.copy()

# Sample large datasets for responsive chart rendering.
MAX_ROWS = 5000

if len(df) > MAX_ROWS:
    st.info(
        f"O dataset tem {len(df):,} linhas. Os gráficos usarão uma "
        f"amostra reproduzível de {MAX_ROWS:,} linhas por desempenho. "
        "A exploração dos dados e a exportação em CSV mantêm o "
        "dataset filtrado completo."
    )

    # Use the same sample for charts and analysis.
    # Filtering and export will operate on the full dataset below.
    chart_source = df.sample(
        n=MAX_ROWS,
        random_state=42
    )
else:
    chart_source = df.copy()


# ==========================================================
# COLUMN CLASSIFICATION
# ==========================================================

numeric_cols = df.select_dtypes(
    include="number"
).columns.tolist()

categorical_cols = df.select_dtypes(
    include=["object", "category", "bool", "string"]
).columns.tolist()

datetime_cols = df.select_dtypes(
    include=["datetime", "datetimetz"]
).columns.tolist()

# Include likely date columns stored as text.
for col in df.select_dtypes(
    include=["object", "string"]
).columns:
    if col not in datetime_cols:
        name = str(col).lower()

        if any(word in name for word in [
            "date", "datetime", "timestamp"
        ]):
            parsed = pd.to_datetime(
                df[col], errors="coerce"
            )

            if parsed.notna().mean() >= 0.8:
                datetime_cols.append(col)


# ==========================================================
# SIDEBAR FILTERS
# ==========================================================

st.sidebar.title("🎛️ Controles do Dashboard")
st.sidebar.caption("Os filtros se aplicam ao dataset completo.")

filtered_df = df.copy()

with st.sidebar.expander(
    "🔎 Filtros por Categoria",
    expanded=True
):
    filter_cols = [
        col for col in categorical_cols
        if df[col].nunique(dropna=True) <= 100
    ]

    for col in filter_cols:
        values = df[col].dropna().unique().tolist()

        if not values:
            continue

        selected = st.multiselect(
            f"{col}",
            options=values,
            key=f"interactive_filter_{col}",
        )

        if selected:
            filtered_df = filtered_df[
                filtered_df[col].isin(selected)
            ]


with st.sidebar.expander("📏 Filtros Numéricos"):
    for col in numeric_cols:
        series = pd.to_numeric(
            filtered_df[col],
            errors="coerce"
        ).dropna()

        if series.empty:
            continue

        minimum = float(series.min())
        maximum = float(series.max())

        if minimum >= maximum:
            continue

        low, high = st.slider(
            f"{col}",
            min_value=minimum,
            max_value=maximum,
            value=(minimum, maximum),
            key=f"interactive_range_{col}",
        )

        filtered_df = filtered_df[
            filtered_df[col].between(low, high)
            | filtered_df[col].isna()
        ]


if filtered_df.empty:
    st.warning(
        "Nenhum registro corresponde aos "
        "filtros. Ajuste as seleções na "
        "barra lateral."
    )
    st.stop()


# ==========================================================
# DATASET OVERVIEW
# ==========================================================

st.subheader("📌 Visão Geral do Dataset")

k1, k2, k3, k4 = st.columns(4)

k1.metric(
    "Registros Filtrados",
    f"{len(filtered_df):,}"
)

k2.metric(
    "Total de Colunas",
    f"{len(filtered_df.columns):,}"
)

k3.metric(
    "Células Ausentes",
    f"{int(filtered_df.isna().sum().sum()):,}"
)

k4.metric(
    "Linhas Duplicadas",
    f"{int(filtered_df.duplicated().sum()):,}"
)

st.caption(
    f"Exibindo {len(filtered_df):,} de {len(df):,} registros originais."
)

st.divider()


# ==========================================================
# DASHBOARD TABS
# ==========================================================

overview_tab, builder_tab, explorer_tab, quality_tab = st.tabs(
    [
        "📈 Visão Geral",
        "🛠️ Construtor de Gráficos",
        "🗂️ Explorador de Dados",
        "🧪 Qualidade dos Dados",
    ]
)


# ==========================================================
# TAB 1: AUTOMATIC VISUALIZATIONS
# ==========================================================

with overview_tab:

    st.subheader("Análise de Distribuição")

    left, right = st.columns(2)

    # ------------------------------------------------------
    # HISTOGRAM
    # ------------------------------------------------------

    with left:
        if numeric_cols:
            hist_col = st.selectbox(
                "Coluna numérica",
                numeric_cols,
                key="overview_hist_column",
            )

            fig = px.histogram(
                filtered_df,
                x=hist_col,
                nbins=30,
                marginal="box",
                title=f"Distribuição de {hist_col}",
                template="plotly_white",
            )

            fig.update_layout(
                height=400,
                showlegend=False,
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
            )
        else:
            st.info(
                "Não há colunas numéricas disponíveis para um histograma."
            )

    # ------------------------------------------------------
    # PIE CHART
    # ------------------------------------------------------

    with right:
        if categorical_cols:
            pie_col = st.selectbox(
                "Coluna categórica",
                categorical_cols,
                key="overview_pie_column",
            )

            counts = (
                filtered_df[pie_col]
                .fillna("(Ausente)")
                .astype(str)
                .value_counts()
                .head(10)
                .rename_axis("Categoria")
                .reset_index(name="Contagem")
            )

            fig = px.pie(
                counts,
                names="Categoria",
                values="Contagem",
                hole=0.45,
                title=f"Principais Categorias: {pie_col}",
                template="plotly_white",
            )

            fig.update_layout(height=400)

            st.plotly_chart(
                fig,
                use_container_width=True,
            )
        else:
            st.info(
                "Não há colunas categóricas disponíveis para um gráfico de pizza."
            )

    # ------------------------------------------------------
    # SCATTER PLOT
    # ------------------------------------------------------

    st.divider()
    st.subheader("Análise de Relação")

    if len(numeric_cols) >= 2:
        c1, c2, c3 = st.columns(3)

        with c1:
            scatter_x = st.selectbox(
                "Eixo X",
                numeric_cols,
                index=0,
                key="overview_scatter_x",
            )

        with c2:
            y_index = (
                1 if numeric_cols[0] == scatter_x else 0
            )

            scatter_y = st.selectbox(
                "Eixo Y",
                numeric_cols,
                index=y_index,
                key="overview_scatter_y",
            )

        with c3:
            scatter_color = st.selectbox(
                "Colorir por",
                ["Nenhum"] + categorical_cols,
                key="overview_scatter_color",
            )

        plot_df = filtered_df

        if len(plot_df) > MAX_ROWS:
            plot_df = plot_df.sample(
                MAX_ROWS,
                random_state=42
            )

        fig = px.scatter(
            plot_df,
            x=scatter_x,
            y=scatter_y,
            color=(
                scatter_color
                if scatter_color != "Nenhum"
                else None
            ),
            hover_data=[scatter_x, scatter_y],
            title=f"{scatter_x} vs {scatter_y}",
            template="plotly_white",
        )

        fig.update_layout(height=500)

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

    else:
        st.info(
            "São necessárias pelo menos duas colunas "
            "numéricas para um gráfico de dispersão."
        )

    # ------------------------------------------------------
    # CORRELATION HEATMAP
    # ------------------------------------------------------

    st.divider()
    st.subheader("Mapa de Calor de Correlação")

    if len(numeric_cols) >= 2:
        heatmap_cols = st.multiselect(
            "Escolha as variáveis numéricas",
            numeric_cols,
            default=numeric_cols[:min(10, len(numeric_cols))],
            key="overview_heatmap_cols",
        )

        if len(heatmap_cols) >= 2:
            corr = filtered_df[heatmap_cols].corr()

            fig = px.imshow(
                corr,
                text_auto=".2f",
                color_continuous_scale="RdBu_r",
                zmin=-1,
                zmax=1,
                aspect="auto",
                title="Matriz de Correlação das Variáveis",
            )

            fig.update_layout(
                height=max(400, len(heatmap_cols) * 40)
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
            )

            upper_triangle = corr.where(
                np.triu(
                    np.ones(corr.shape),
                    k=1
                ).astype(bool)
            ).stack()

            if not upper_triangle.empty:
                pair = upper_triangle.abs().idxmax()
                coefficient = upper_triangle.loc[pair]

                st.info(
                    "Correlação absoluta mais forte: "
                    f"{pair[0]} e {pair[1]} (r = {coefficient:.3f}). "
                    "Correlação não implica causalidade."
                )
        else:
            st.info(
                "Selecione pelo menos duas colunas para a análise de correlação."
            )
    else:
        st.info(
            "A análise de correlação exige pelo menos duas colunas numéricas."
        )


# ==========================================================
# TAB 2: INTERACTIVE CHART BUILDER
# ==========================================================

with builder_tab:

    st.subheader("🛠️ Construtor de Gráficos Personalizados")

    chart_type = st.selectbox(
        "Escolha a visualização",
        [
            "Gráfico de Dispersão",
            "Gráfico de Linhas",
            "Gráfico de Barras",
            "Histograma",
            "Box Plot",
            "Gráfico de Violino",
            "Gráfico de Pizza",
            "Mapa de Calor de Correlação",
        ],
        key="builder_chart_type",
    )

    # ------------------------------------------------------
    # HISTOGRAM
    # ------------------------------------------------------

    if chart_type == "Histograma":

        if numeric_cols:
            x_col = st.selectbox(
                "Coluna numérica",
                numeric_cols,
                key="builder_hist_x",
            )

            bins = st.slider(
                "Número de faixas",
                min_value=5,
                max_value=100,
                value=30,
                key="builder_hist_bins",
            )

            fig = px.histogram(
                filtered_df,
                x=x_col,
                nbins=bins,
                marginal="box",
                template="plotly_white",
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
            )
        else:
            st.info("O histograma exige uma coluna numérica.")

    # ------------------------------------------------------
    # PIE CHART
    # ------------------------------------------------------

    elif chart_type == "Gráfico de Pizza":

        if categorical_cols:
            x_col = st.selectbox(
                "Coluna categórica",
                categorical_cols,
                key="builder_pie_x",
            )

            top_n = st.slider(
                "Máximo de categorias",
                min_value=3,
                max_value=20,
                value=10,
                key="builder_pie_top_n",
            )

            counts = (
                filtered_df[x_col]
                .fillna("(Ausente)")
                .astype(str)
                .value_counts()
                .head(top_n)
                .rename_axis("Categoria")
                .reset_index(name="Contagem")
            )

            fig = px.pie(
                counts,
                names="Categoria",
                values="Contagem",
                hole=0.4,
                template="plotly_white",
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
            )
        else:
            st.info("O gráfico de pizza exige uma coluna categórica.")

    # ------------------------------------------------------
    # CORRELATION HEATMAP
    # ------------------------------------------------------

    elif chart_type == "Mapa de Calor de Correlação":

        if len(numeric_cols) >= 2:
            selected_cols = st.multiselect(
                "Variáveis numéricas",
                numeric_cols,
                default=numeric_cols[:min(10, len(numeric_cols))],
                key="builder_heatmap_cols",
            )

            if len(selected_cols) >= 2:
                fig = px.imshow(
                    filtered_df[selected_cols].corr(),
                    text_auto=".2f",
                    color_continuous_scale="RdBu_r",
                    zmin=-1,
                    zmax=1,
                    aspect="auto",
                    template="plotly_white",
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True,
                )
            else:
                st.info("Selecione pelo menos duas colunas numéricas.")
        else:
            st.info("São necessárias pelo menos duas colunas numéricas.")

    # ------------------------------------------------------
    # SCATTER, LINE, BAR, BOX, VIOLIN
    # ------------------------------------------------------

    else:

        x_options = list(
            dict.fromkeys(
                categorical_cols
                + numeric_cols
                + datetime_cols
            )
        )

        if not x_options or not numeric_cols:
            st.info(
                "Este gráfico exige colunas adequadas para o eixo X e numéricas."
            )
        else:
            c1, c2 = st.columns(2)

            with c1:
                x_col = st.selectbox(
                    "Eixo X",
                    x_options,
                    key="builder_x",
                )

            with c2:
                y_col = st.selectbox(
                    "Eixo Y",
                    numeric_cols,
                    key="builder_y",
                )

            color_col = st.selectbox(
                "Agrupar / Colorir por",
                ["Nenhum"] + categorical_cols,
                key="builder_color",
            )

            plot_df = filtered_df

            if len(plot_df) > MAX_ROWS:
                plot_df = plot_df.sample(
                    MAX_ROWS,
                    random_state=42
                )

            color_arg = (
                color_col
                if color_col != "Nenhum"
                else None
            )

            if chart_type == "Gráfico de Dispersão":

                fig = px.scatter(
                    plot_df,
                    x=x_col,
                    y=y_col,
                    color=color_arg,
                    template="plotly_white",
                )

            elif chart_type == "Gráfico de Linhas":

                fig = px.line(
                    plot_df,
                    x=x_col,
                    y=y_col,
                    color=color_arg,
                    template="plotly_white",
                )

            elif chart_type == "Gráfico de Barras":

                aggregation = st.selectbox(
                    "Agregação",
                    ["Soma", "Média", "Mediana", "Contagem"],
                    key="builder_bar_aggregation",
                )

                if aggregation == "Contagem":
                    plot_df = (
                        plot_df.groupby(
                            x_col,
                            dropna=False,
                        )[y_col]
                        .count()
                        .reset_index(name="Contagem")
                    )

                    fig = px.bar(
                        plot_df,
                        x=x_col,
                        y="Contagem",
                        template="plotly_white",
                    )

                else:
                    agg_func = {
                        "Soma": "sum",
                        "Média": "mean",
                        "Mediana": "median",
                    }[aggregation]

                    plot_df = (
                        plot_df.groupby(
                            x_col,
                            dropna=False,
                        )[y_col]
                        .agg(agg_func)
                        .reset_index()
                    )

                    fig = px.bar(
                        plot_df,
                        x=x_col,
                        y=y_col,
                        template="plotly_white",
                    )

            elif chart_type == "Box Plot":

                fig = px.box(
                    plot_df,
                    x=x_col,
                    y=y_col,
                    color=color_arg,
                    template="plotly_white",
                )

            else:

                fig = px.violin(
                    plot_df,
                    x=x_col,
                    y=y_col,
                    color=color_arg,
                    box=True,
                    template="plotly_white",
                )

            fig.update_layout(height=520)

            st.plotly_chart(
                fig,
                use_container_width=True,
            )


# ==========================================================
# TAB 3: DATA EXPLORER
# ==========================================================

with explorer_tab:

    st.subheader("🗂️ Explorador de Dados")

    st.caption(
        "Inspecione os registros filtrados e baixe os dados selecionados."
    )

    selected_columns = st.multiselect(
        "Colunas a exibir",
        options=filtered_df.columns.tolist(),
        default=filtered_df.columns.tolist()[
            :min(10, len(filtered_df.columns))
        ],
        key="explorer_columns",
    )

    if selected_columns:
        st.dataframe(
            filtered_df[selected_columns],
            use_container_width=True,
            height=420,
        )
    else:
        st.info("Selecione pelo menos uma coluna.")

    st.markdown("#### Resumo Estatístico")

    summary = filtered_df.describe(
        include="all"
    ).transpose()

    st.dataframe(
        summary,
        use_container_width=True,
    )

    st.download_button(
        label="⬇️ Baixar dataset filtrado (CSV)",
        data=filtered_df.to_csv(
            index=False
        ).encode("utf-8"),
        file_name="filtered_dataset.csv",
        mime="text/csv",
        use_container_width=True,
    )


# ==========================================================
# TAB 4: DATA QUALITY
# ==========================================================

with quality_tab:

    st.subheader("🧪 Relatório de Qualidade dos Dados")

    missing_report = pd.DataFrame({
        "Coluna": filtered_df.columns,
        "Valores Ausentes": (
            filtered_df.isna().sum().values
        ),
        "% Ausentes": (
            filtered_df.isna().mean().values * 100
        ).round(2),
        "Valores Únicos": (
            filtered_df.nunique(dropna=True).values
        ),
        "Tipo de Dado": (
            filtered_df.dtypes.astype(str).values
        ),
    }).sort_values(
        "% Ausentes",
        ascending=False,
    )

    st.markdown("#### Valores Ausentes por Coluna")

    st.dataframe(
        missing_report,
        use_container_width=True,
    )

    missing_only = missing_report[
        missing_report["Valores Ausentes"] > 0
    ]

    if not missing_only.empty:

        fig = px.bar(
            missing_only,
            x="Coluna",
            y="% Ausentes",
            title="Percentual de Dados Ausentes",
            template="plotly_white",
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

    else:
        st.success("Nenhum valor ausente nos dados filtrados.")

    # ------------------------------------------------------
    # DUPLICATE ROWS
    # ------------------------------------------------------

    st.markdown("#### Registros Duplicados")

    duplicate_count = int(
        filtered_df.duplicated().sum()
    )

    st.metric(
        "Linhas Duplicadas",
        f"{duplicate_count:,}",
    )

    # ------------------------------------------------------
    # OUTLIER DETECTION
    # ------------------------------------------------------

    st.markdown("#### Possíveis Outliers Numéricos")

    outlier_rows = []

    for col in numeric_cols:

        series = filtered_df[col].dropna()

        if series.empty:
            continue

        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1

        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr

        count = int(
            (
                (series < lower)
                | (series > upper)
            ).sum()
        )

        outlier_rows.append({
            "Coluna": col,
            "Possíveis Outliers": count,
            "Limite Inferior": round(float(lower), 3),
            "Limite Superior": round(float(upper), 3),
        })

    if outlier_rows:

        st.dataframe(
            pd.DataFrame(outlier_rows),
            use_container_width=True,
        )

        st.caption(
            "Os outliers usam a regra de 1,5 × IQR. "
            "Valores sinalizados não são necessariamente "
            "erros."
        )

    else:
        st.info("Não há colunas numéricas disponíveis para a análise de outliers.")

    # ------------------------------------------------------
    # AUTOMATED DATA SUMMARY
    # ------------------------------------------------------

    st.markdown("#### Resumo Automático")

    total_cells = (
        len(filtered_df) * len(filtered_df.columns)
    )

    missing_cells = int(
        filtered_df.isna().sum().sum()
    )

    missing_pct = (
        missing_cells / total_cells * 100
        if total_cells else 0
    )

    st.write(f"**Registros analisados:** {len(filtered_df):,}")
    st.write(f"**Colunas numéricas:** {len(numeric_cols)}")
    st.write(f"**Colunas categóricas:** {len(categorical_cols)}")
    st.write(f"**Células ausentes:** {missing_cells:,}")
    st.write(f"**Taxa de células ausentes:** {missing_pct:.2f}%")
    st.write(f"**Linhas duplicadas:** {duplicate_count:,}")

    if len(numeric_cols) >= 2:

        corr = filtered_df[numeric_cols].corr()

        pairs = corr.where(
            np.triu(
                np.ones(corr.shape),
                k=1,
            ).astype(bool)
        ).stack()

        if not pairs.empty:

            pair = pairs.abs().idxmax()
            value = pairs.loc[pair]

            st.write(
                "**Correlação absoluta mais forte:** "
                f"{pair[0]} vs {pair[1]} (r = {value:.3f})"
            )

    ai_insight(
        "Explore distribuições, correlações, valores ausentes, duplicados "
        "e possíveis outliers para entender seus dados. Trate padrões "
        "estatísticos como indícios a investigar, não como prova "
        "de causalidade."
    )

# ==========================================================
# CUSTOM NAVIGATION BAR
# ==========================================================

if "dashboard_page" not in st.session_state:
    st.session_state["dashboard_page"] = "Overview"

st.markdown(
    """
    <style>
    div.stButton > button {
        border-radius: 10px;
        min-height: 44px;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

nav_items = [
    ("Overview", "📈 Visão Geral"),
    ("Chart Builder", "🛠️ Construtor de Gráficos"),
    ("Data Explorer", "🗂️ Explorador de Dados"),
    ("Data Quality", "🧪 Qualidade dos Dados"),
]

nav_cols = st.columns(4)

for col, (page_key, label) in zip(nav_cols, nav_items):
    with col:
        if st.button(
            label,
            key=f"nav_{page_key}",
            use_container_width=True,
            type=(
                "primary"
                if st.session_state["dashboard_page"] == page_key
                else "secondary"
            ),
        ):
            st.session_state["dashboard_page"] = page_key
            st.rerun()

st.divider()

current_page = st.session_state["dashboard_page"]
# =========================================================
# PREVIOUS / NEXT PAGE NAVIGATION
# Keep this at the very bottom of app/pages/7_Prediction.py.
# =========================================================
st.divider()
nav_previous, nav_spacer, nav_next = st.columns([1, 2, 1])

with nav_previous:
    if st.button(
        "⬅️ Anterior: Predição",
        key="page7_previous_navigation",
        use_container_width=True,
    ):
        st.switch_page("pages/7_Prediction.py")

with nav_next:
    if st.button(
        "Próximo: Chat com IA ➡️",
        key="page7_next_navigation",
        use_container_width=True,
    ):
        st.switch_page("pages/11_AI_Chat.py")


# ==========================================================
# FOOTER
# ==========================================================

page_footer()
