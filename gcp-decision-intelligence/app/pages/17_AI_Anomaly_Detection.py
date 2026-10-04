
import streamlit as st
import pandas as pd
import plotly.express as px

from src.anomaly_detection.anomaly_detector import AnomalyDetector
from src.ui.layout import page_header, ai_insight, page_footer


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Detecção de Anomalias com IA | NexDecision AI",
    page_icon="🚨",
    layout="wide"
)

page_header(
    "🚨 Detecção de Anomalias com IA",
    "Descubra padrões incomuns, investigue registros suspeitos "
    "e exporte os achados para análises adicionais."
)

st.caption(
    "Identifique registros que fogem dos padrões do seu dataset. Uma anomalia "
    "é um sinal para investigar, não prova de fraude ou erro."
)

st.markdown("---")


# --------------------------------------------------
# CUSTOM STYLING
# --------------------------------------------------

st.markdown(
    """
    <style>
    div[data-testid="stMetric"] {
        background: rgba(128, 128, 128, 0.08);
        border: 1px solid rgba(128, 128, 128, 0.20);
        padding: 16px;
        border-radius: 12px;
    }

    .section-description {
        color: #888888;
        font-size: 0.9rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# --------------------------------------------------
# CHECK DATASET
# --------------------------------------------------

if "dataset" not in st.session_state:
    st.warning(
        "⚠️ Nenhum dataset encontrado. Envie um dataset antes "
        "de executar a detecção de anomalias."
    )

    if st.button("🏠 Ir para o Início"):
        st.switch_page("pages/0_Home.py")

    st.stop()

df = st.session_state["dataset"]

if not isinstance(df, pd.DataFrame) or df.empty:
    st.error(
        "O dataset atual está vazio ou é inválido. "
        "Envie um dataset com dados e tente novamente."
    )
    st.stop()

st.success("✅ Dataset carregado com sucesso")


# --------------------------------------------------
# DATASET OVERVIEW
# --------------------------------------------------

st.subheader("📊 Visão Geral do Dataset")

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric("📄 Total de Linhas", f"{len(df):,}")

with c2:
    st.metric("📊 Total de Colunas", f"{len(df.columns):,}")

with c3:
    st.metric(
        "⚠️ Valores Ausentes",
        f"{int(df.isna().sum().sum()):,}"
    )

with c4:
    st.metric(
        "🔁 Linhas Duplicadas",
        f"{int(df.duplicated().sum()):,}"
    )

numeric_columns = df.select_dtypes(
    include="number"
).columns.tolist()

st.caption(
    f"Variáveis numéricas disponíveis: {len(numeric_columns)}"
)

st.markdown("---")


# --------------------------------------------------
# RUN ANOMALY DETECTION
# --------------------------------------------------

st.subheader("🔍 Motor de Detecção")

st.markdown(
    '<p class="section-description">Execute o detector de anomalias '
    'no dataset atual.</p>',
    unsafe_allow_html=True
)

run_detection = st.button(
    "🚀 Executar detecção de anomalias",
    type="primary",
    use_container_width=False
)

if run_detection:
    try:
        with st.spinner("Analisando os dados em busca de padrões incomuns..."):
            detector = AnomalyDetector()
            result = detector.detect(df.copy())

        if result is None:
            st.session_state.pop(
                "anomaly_detection_result",
                None
            )
            st.error(
                "O detector não conseguiu gerar um resultado. Verifique "
                "se o dataset tem colunas numéricas utilizáveis."
            )

        elif not isinstance(result, pd.DataFrame):
            st.session_state.pop(
                "anomaly_detection_result",
                None
            )
            st.error(
                "O detector retornou um formato inesperado. Era "
                "esperado um DataFrame pandas."
            )

        elif "Anomalia" not in result.columns:
            st.session_state.pop(
                "anomaly_detection_result",
                None
            )
            st.error(
                "A saída do detector não contém a coluna obrigatória "
                "'Anomalia'. Verifique o anomaly_detector.py."
            )

        elif result.empty:
            st.session_state["anomaly_detection_result"] = result
            st.info("O detector não retornou registros.")

        else:
            st.session_state["anomaly_detection_result"] = result
            st.success("✅ Detecção de anomalias concluída.")

    except Exception as error:
        st.error(f"Falha na detecção de anomalias: {error}")


# --------------------------------------------------
# LOAD LATEST RESULTS
# --------------------------------------------------

if "anomaly_detection_result" not in st.session_state:
    st.info(
        "Selecione **Executar detecção de anomalias** para analisar seu dataset."
    )
    st.stop()

result = st.session_state["anomaly_detection_result"].copy()

if result.empty:
    st.info("O detector não retornou registros.")
    st.stop()

if "Anomalia" not in result.columns:
    st.error(
        "O resultado salvo não tem a coluna Anomalia. Execute "
        "a detecção novamente."
    )
    st.stop()


# --------------------------------------------------
# NORMALISE RESULT LABELS
# --------------------------------------------------

result["Anomalia"] = (
    result["Anomalia"]
    .astype(str)
    .str.strip()
    .str.title()
)

anomaly_df = result[
    result["Anomalia"] == "Anomalia"
].copy()

normal_df = result[
    result["Anomalia"] == "Normal"
].copy()

other_df = result[
    ~result["Anomalia"].isin(["Anomalia", "Normal"])
].copy()

total = len(result)
anomalies = len(anomaly_df)
normal = len(normal_df)
other = len(other_df)

percentage = (
    round((anomalies / total) * 100, 2)
    if total > 0
    else 0
)


# --------------------------------------------------
# ANOMALY SUMMARY
# --------------------------------------------------

st.markdown("---")
st.subheader("📈 Resumo da Detecção")

k1, k2, k3, k4 = st.columns(4)

with k1:
    st.metric("Total Analisado", f"{total:,}")

with k2:
    st.metric("Registros Normais", f"{normal:,}")

with k3:
    st.metric(
        "Anomalias Detectadas",
        f"{anomalies:,}",
        delta=f"{percentage}% dos registros",
        delta_color="inverse"
    )

with k4:
    st.metric("Outros Rótulos", f"{other:,}")

st.progress(
    min(max(percentage / 100, 0.0), 1.0),
    text=f"Proporção de anomalias: {percentage}%"
)

st.caption(
    "O percentual de anomalias é a proporção de registros "
    "rotulados como 'Anomalia' pelo detector. Não é uma probabilidade "
    "de fraude."
)


# --------------------------------------------------
# RESULT FILTERS
# --------------------------------------------------

st.markdown("---")
st.subheader("🔎 Explorar Resultados da Detecção")

filter_col, search_col = st.columns([1, 2])

with filter_col:
    label_options = sorted(
        result["Anomalia"].dropna().unique().tolist()
    )

    selected_labels = st.multiselect(
        "Classificação do registro",
        options=label_options,
        default=label_options
    )

with search_col:
    record_search = st.text_input(
        "Buscar nos resultados",
        placeholder="Buscar em todos os valores do resultado..."
    )

filtered_result = result[
    result["Anomalia"].isin(selected_labels)
].copy()

if record_search.strip():
    query = record_search.strip().lower()

    row_matches = filtered_result.astype(str).apply(
        lambda column: column.str.lower().str.contains(
            query,
            na=False,
            regex=False
        )
    ).any(axis=1)

    filtered_result = filtered_result[row_matches]

st.caption(
    f"Exibindo {len(filtered_result):,} de {len(result):,} registros."
)


# --------------------------------------------------
# RESULT TABLE
# --------------------------------------------------

st.subheader("📋 Resultados da Detecção")

st.dataframe(
    filtered_result,
    use_container_width=True,
    hide_index=True,
    height=350
)


# --------------------------------------------------
# ANOMALY-ONLY TABLE
# --------------------------------------------------

st.markdown("---")
st.subheader("🚨 Investigação de Anomalias")

if anomaly_df.empty:
    st.success(
        "Nenhum registro foi rotulado como anomalia nesta execução."
    )

else:
    st.write(
        f"Foram encontrados **{len(anomaly_df):,}** registros para revisão."
    )

    with st.expander(
        "Ver registros de anomalias detectados",
        expanded=True
    ):
        st.dataframe(
            anomaly_df,
            use_container_width=True,
            hide_index=True,
            height=300
        )

    if numeric_columns:
        available_features = [
            column
            for column in numeric_columns
            if column in anomaly_df.columns
        ]

        if available_features:
            selected_feature = st.selectbox(
                "Inspecionar uma variável das anomalias",
                options=available_features
            )

            feature_values = pd.to_numeric(
                anomaly_df[selected_feature],
                errors="coerce"
            ).dropna()

            if not feature_values.empty:
                st.metric(
                    f"Média de {selected_feature} nas anomalias",
                    f"{feature_values.mean():,.3f}"
                )

                st.caption(
                    "Esta estatística descreve apenas os registros sinalizados; "
                    "compare-a com os registros normais antes de tirar conclusões."
                )


# --------------------------------------------------
# VISUAL ANALYTICS
# --------------------------------------------------

st.markdown("---")
st.subheader("📊 Análise das Anomalias")

chart_left, chart_right = st.columns(2)

with chart_left:
    st.markdown("#### Normal vs Anomalia")

    distribution = (
        result["Anomalia"]
        .value_counts()
        .rename_axis("Classificação")
        .reset_index(name="Registros")
    )

    pie_fig = px.pie(
        distribution,
        names="Classificação",
        values="Registros",
        hole=0.48
    )

    pie_fig.update_layout(
        margin=dict(l=10, r=10, t=25, b=10)
    )

    st.plotly_chart(
        pie_fig,
        use_container_width=True
    )

with chart_right:
    st.markdown("#### Contagem por Classificação")

    bar_fig = px.bar(
        distribution,
        x="Classificação",
        y="Registros",
        text="Registros"
    )

    bar_fig.update_layout(
        xaxis_title="Classificação",
        yaxis_title="Número de Registros",
        showlegend=False,
        margin=dict(l=10, r=10, t=25, b=10)
    )

    bar_fig.update_traces(
        textposition="outside"
    )

    st.plotly_chart(
        bar_fig,
        use_container_width=True
    )


# --------------------------------------------------
# NUMERIC FEATURE COMPARISON
# --------------------------------------------------

st.markdown("---")
st.subheader("📉 Comparação de Variáveis Numéricas")

shared_numeric = [
    column
    for column in numeric_columns
    if column in result.columns
]

if shared_numeric and result["Anomalia"].nunique() > 1:

    selected_numeric = st.selectbox(
        "Escolha uma variável numérica",
        options=shared_numeric,
        key="anomaly_feature_comparison"
    )

    comparison_df = result.copy()

    comparison_df[selected_numeric] = pd.to_numeric(
        comparison_df[selected_numeric],
        errors="coerce"
    )

    comparison_df = comparison_df.dropna(
        subset=[selected_numeric]
    )

    if not comparison_df.empty:

        box_fig = px.box(
            comparison_df,
            x="Anomalia",
            y=selected_numeric,
            color="Anomalia",
            points="outliers",
            title=f"{selected_numeric}: Normal vs Anomalia"
        )

        box_fig.update_layout(
            xaxis_title="Classificação do detector",
            yaxis_title=selected_numeric
        )

        st.plotly_chart(
            box_fig,
            use_container_width=True
        )

        st.caption(
            "Este gráfico compara os valores das variáveis por "
            "rótulo do detector. Ele não estabelece a causa de "
            "uma anomalia."
        )

else:
    st.info(
        "A comparação de variáveis exige colunas numéricas nos resultados "
        "da detecção e pelo menos dois grupos de classificação."
    )


# --------------------------------------------------
# DOWNLOAD REPORTS
# --------------------------------------------------

st.markdown("---")
st.subheader("📥 Exportar Relatórios de Detecção")

export_all_col, export_anomaly_col = st.columns(2)

with export_all_col:
    st.download_button(
        "📄 Baixar resultados completos da detecção",
        data=result.to_csv(index=False).encode("utf-8"),
        file_name="nexdecision_full_detection_report.csv",
        mime="text/csv",
        use_container_width=True
    )

with export_anomaly_col:
    st.download_button(
        "🚨 Baixar relatório só com anomalias",
        data=anomaly_df.to_csv(index=False).encode("utf-8"),
        file_name="nexdecision_anomaly_report.csv",
        mime="text/csv",
        use_container_width=True
    )


# --------------------------------------------------
# BUSINESS INTERPRETATION
# --------------------------------------------------

st.markdown("---")
st.subheader("🤖 Interpretação e Próximos Passos")

if anomalies == 0:
    st.info(
        "O detector não rotulou nenhum registro como anomalia. Isso "
        "não garante que todos os registros estejam corretos ou normais."
    )

elif percentage < 5:
    st.info(
        f"{percentage}% dos registros foram sinalizados. Comece revisando "
        "as linhas sinalizadas, verificando a qualidade dos dados "
        "e comparando suas variáveis com os registros normais."
    )

elif percentage < 15:
    st.warning(
        f"{percentage}% dos registros foram sinalizados. Investigue padrões "
        "recorrentes, valores incomuns e possíveis mudanças na coleta "
        "de dados ou nas operações do negócio."
    )

else:
    st.warning(
        f"{percentage}% dos registros foram sinalizados. Revise a saída "
        "do detector e as características do dataset antes de tratar "
        "isso como um problema operacional. Uma taxa alta de anomalias "
        "também pode refletir a distribuição dos dados ou as configurações "
        "do detector."
    )

ai_insight(
    "A detecção de anomalias destaca registros que diferem dos padrões "
    "aprendidos ou configurados. Investigue os registros sinalizados "
    "com o contexto do negócio antes de tomar decisões operacionais. "
    "Quando possível, valide o detector com exemplos rotulados."
)


# --------------------------------------------------
# PAGE NAVIGATION
# --------------------------------------------------

st.markdown("---")
st.subheader("🧭 Continue Explorando o NexDecision AI")

prev_col, home_col, next_col = st.columns(3)

with prev_col:
    if st.button(
        "⬅️ Histórico de Predições",
        use_container_width=True
    ):
        st.switch_page("pages/14_Prediction_History.py")

with home_col:
    if st.button(
        "🏠 Início",
        use_container_width=True
    ):
        st.switch_page("pages/0_Home.py")

with next_col:
    if st.button(
        "➡️ Relatório Executivo",
        use_container_width=True
    ):
        st.switch_page("pages/18_Executive_Report.py")


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

page_footer()
