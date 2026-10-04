
import os
import streamlit as st
import pandas as pd
import plotly.express as px

from src.ui.layout import page_header, ai_insight, page_footer
from src.executive_reports.report_builder import ExecutiveReportBuilder


# ------------------------------------------------
# PAGE CONFIGURATION
# ------------------------------------------------

st.set_page_config(
    page_title="Relatório Executivo | NexDecision AI",
    page_icon="📄",
    layout="wide"
)

page_header(
    "📄 Gerador de Relatório Executivo",
    "Crie relatórios prontos para a gestão a partir das métricas "
    "de qualidade do dataset e do seu fluxo de análise com IA."
)

st.caption(
    "Revise a qualidade dos dados, entenda os riscos potenciais "
    "e exporte um relatório em PDF para as partes interessadas "
    "do negócio."
)

st.markdown("---")


# ------------------------------------------------
# CUSTOM STYLING
# ------------------------------------------------

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


# ------------------------------------------------
# CHECK DATASET
# ------------------------------------------------

if "dataset" not in st.session_state:
    st.warning(
        "Nenhum dataset carregado. Envie um dataset antes de "
        "gerar um relatório executivo."
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


# ------------------------------------------------
# DATASET STATISTICS
# ------------------------------------------------

rows = len(df)
columns = len(df.columns)
missing = int(df.isnull().sum().sum())
duplicates = int(df.duplicated().sum())

numeric_columns = df.select_dtypes(
    include="number"
).columns.tolist()

categorical_columns = df.select_dtypes(
    include=["object", "category", "string"]
).columns.tolist()

missing_percentage = (
    round((missing / (rows * columns)) * 100, 2)
    if rows > 0 and columns > 0
    else 0
)

duplicate_percentage = (
    round((duplicates / rows) * 100, 2)
    if rows > 0
    else 0
)

dataset_summary = {
    "Rows": rows,
    "Columns": columns,
    "Missing": missing,
    "Duplicates": duplicates
}


# ------------------------------------------------
# DATA QUALITY SCORE
# ------------------------------------------------
# A simple heuristic, not a validated business score.
# ------------------------------------------------

health = 100

health -= min(missing_percentage * 0.7, 50)
health -= min(duplicate_percentage * 0.5, 30)

health = max(0, min(100, round(health)))

if health >= 90:
    grade = "Excelente"
elif health >= 75:
    grade = "Bom"
elif health >= 60:
    grade = "Requer atenção"
else:
    grade = "Fraco"


# ------------------------------------------------
# EXECUTIVE SUMMARY
# ------------------------------------------------

st.subheader("📊 Visão Geral Executiva")

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric("📄 Total de Registros", f"{rows:,}")

with c2:
    st.metric("📊 Total de Variáveis", f"{columns:,}")

with c3:
    st.metric(
        "⚠️ Valores Ausentes",
        f"{missing:,}",
        delta=f"{missing_percentage}% das células",
        delta_color="inverse"
    )

with c4:
    st.metric(
        "🔁 Linhas Duplicadas",
        f"{duplicates:,}",
        delta=f"{duplicate_percentage}% das linhas",
        delta_color="inverse"
    )

st.markdown("---")

score_col, grade_col, numeric_col, category_col = st.columns(4)

with score_col:
    st.metric(
        "Score de Qualidade do Dataset",
        f"{health}/100"
    )

with grade_col:
    st.metric(
        "Categoria de Qualidade",
        grade
    )

with numeric_col:
    st.metric(
        "Variáveis Numéricas",
        len(numeric_columns)
    )

with category_col:
    st.metric(
        "Variáveis Categóricas",
        len(categorical_columns)
    )

st.progress(
    health / 100,
    text=f"Score heurístico de qualidade do dataset: {health}/100"
)

st.caption(
    "O score é uma heurística interna simples baseada nos percentuais "
    "de células ausentes e linhas duplicadas. Não é uma medida validada "
    "da saúde geral do negócio, da prontidão do modelo ou do desempenho "
    "do negócio."
)

st.markdown("---")


# ------------------------------------------------
# DATA QUALITY VISUALIZATION
# ------------------------------------------------

st.subheader("🔬 Análise de Qualidade do Dataset")

quality_left, quality_right = st.columns(2)

with quality_left:

    st.markdown("#### Células Ausentes vs Disponíveis")

    total_cells = rows * columns
    available_cells = max(0, total_cells - missing)

    quality_chart_df = pd.DataFrame({
        "Situação da Célula": ["Disponíveis", "Ausentes"],
        "Células": [available_cells, missing]
    })

    quality_fig = px.pie(
        quality_chart_df,
        names="Situação da Célula",
        values="Células",
        hole=0.5
    )

    quality_fig.update_layout(
        margin=dict(l=10, r=10, t=20, b=10)
    )

    st.plotly_chart(
        quality_fig,
        use_container_width=True
    )

with quality_right:

    st.markdown("#### Valores Ausentes por Variável")

    missing_by_column = (
        df.isnull()
        .sum()
        .sort_values(ascending=False)
        .head(15)
    )

    missing_df = (
        missing_by_column
        .rename_axis("Variável")
        .reset_index(name="Valores Ausentes")
    )

    missing_df = missing_df[
        missing_df["Valores Ausentes"] > 0
    ]

    if not missing_df.empty:

        missing_fig = px.bar(
            missing_df.sort_values(
                "Valores Ausentes",
                ascending=True
            ),
            x="Valores Ausentes",
            y="Variável",
            orientation="h",
            text="Valores Ausentes"
        )

        missing_fig.update_layout(
            xaxis_title="Número de Valores Ausentes",
            yaxis_title="Variável",
            margin=dict(l=10, r=10, t=20, b=10)
        )

        st.plotly_chart(
            missing_fig,
            use_container_width=True
        )

    else:
        st.success(
            "Nenhum valor ausente foi encontrado no dataset atual."
        )

st.markdown("---")


# ------------------------------------------------
# AUTOMATED QUALITY FINDINGS
# ------------------------------------------------

st.subheader("🧠 Principais Descobertas")

findings = []

if missing == 0:
    findings.append(
        "Nenhuma célula ausente foi encontrada no dataset atual."
    )
else:
    findings.append(
        f"Foram detectadas {missing:,} células "
        f"ausentes ({missing_percentage}% de "
        "todas as células)."
    )

if duplicates == 0:
    findings.append(
        "Nenhuma linha totalmente duplicada foi encontrada."
    )
else:
    findings.append(
        f"Foram encontradas {duplicates:,} linhas totalmente "
        f"duplicadas ({duplicate_percentage}% de todos "
        "os registros)."
    )

findings.append(
    f"O dataset contém {len(numeric_columns)} variáveis "
    f"numéricas e {len(categorical_columns)} categóricas."
)

for finding in findings:
    st.markdown(f"- {finding}")

st.markdown("---")


# ------------------------------------------------
# AUTO ML SUMMARY
# ------------------------------------------------

st.subheader("🤖 Resumo do AutoML")

automl_result = (
    "O status de execução do AutoML e o desempenho dos modelos não "
    "foram obtidos por esta página de relatório. Abra a página AutoML "
    "para ver os modelos avaliados, as métricas e o modelo selecionado."
)

st.info(automl_result)

if st.button(
    "🧪 Abrir AutoML",
    use_container_width=False
):
    st.switch_page("pages/5_AutoML.py")

st.caption(
    "Este relatório não afirma que um melhor modelo foi encontrado, "
    "a menos que os resultados reais do AutoML estejam conectados "
    "ao gerador de relatórios."
)

st.markdown("---")


# ------------------------------------------------
# ANOMALY SUMMARY
# ------------------------------------------------

st.subheader("🚨 Resumo da Detecção de Anomalias")

anomaly_summary = (
    "Os resultados da detecção de anomalias não estão conectados "
    "diretamente a esta página de relatório. Acesse Detecção de Anomalias "
    "com IA para executar o detector e revisar os registros sinalizados."
)

anomaly_result = st.session_state.get(
    "anomaly_detection_result"
)

if isinstance(anomaly_result, pd.DataFrame) and (
    not anomaly_result.empty
    and "Anomalia" in anomaly_result.columns
):

    labels = (
        anomaly_result["Anomalia"]
        .astype(str)
        .str.strip()
        .str.title()
    )

    anomaly_count = int(
        (labels == "Anomalia").sum()
    )

    anomaly_rate = round(
        anomaly_count / len(anomaly_result) * 100,
        2
    )

    anomaly_summary = (
        "O resultado de detecção de anomalias armazenado mais recente "
        f"contém {len(anomaly_result):,} registros analisados, dos "
        f"quais {anomaly_count:,} foram rotulados como anomalias "
        f"({anomaly_rate}%). São rótulos do detector, não fraudes "
        "ou erros confirmados."
    )

    st.info(anomaly_summary)

else:
    st.info(anomaly_summary)

if st.button(
    "🚨 Abrir Detecção de Anomalias com IA",
    use_container_width=False
):
    st.switch_page("pages/17_AI_Anomaly_Detection.py")

st.markdown("---")


# ------------------------------------------------
# RECOMMENDATIONS
# ------------------------------------------------

st.subheader("💡 Próximos Passos Recomendados")

recommendations = []

if missing > 0:
    recommendations.append(
        "Inspecione os valores ausentes por variável e escolha "
        "regras adequadas de imputação ou exclusão antes de "
        "modelar."
    )

if duplicates > 0:
    recommendations.append(
        "Revise os registros duplicados e remova-os apenas quando "
        "representarem duplicação indesejada."
    )

if numeric_columns:
    recommendations.append(
        "Revise as distribuições das variáveis numéricas e possíveis outliers."
    )

if categorical_columns:
    recommendations.append(
        "Verifique a consistência das categorias, diferenças "
        "de grafia e campos de alta cardinalidade."
    )

recommendations.extend([
    "Valide tipos de dados, faixas de valores e regras de negócio.",
    "Compare os modelos candidatos com métricas de validação adequadas.",
    "Acompanhe o desempenho dos modelos e a qualidade dos dados conforme novos dados chegam."
])

for number, recommendation in enumerate(
    recommendations,
    start=1
):
    st.markdown(f"**{number}.** {recommendation}")

st.markdown("---")


# ------------------------------------------------
# REPORT CONFIGURATION
# ------------------------------------------------

st.subheader("⚙️ Configure seu Relatório")

report_title = st.text_input(
    "Título do relatório",
    value="NexDecision AI - Relatório Executivo de Dados"
)

prepared_for = st.text_input(
    "Preparado para / departamento",
    placeholder="ex.: Diretoria, Time de Analytics"
)

include_recommendations = st.checkbox(
    "Incluir recomendações",
    value=True
)

include_anomaly_summary = st.checkbox(
    "Incluir resumo de anomalias",
    value=True
)

final_recommendations = (
    recommendations
    if include_recommendations
    else []
)

final_anomaly_summary = (
    anomaly_summary
    if include_anomaly_summary
    else "Resumo de anomalias excluído pela configuração do relatório."
)

report_filename = st.text_input(
    "Nome do arquivo PDF",
    value="Executive_Report.pdf"
).strip()

if not report_filename:
    report_filename = "Executive_Report.pdf"

if not report_filename.lower().endswith(".pdf"):
    report_filename += ".pdf"

st.caption(
    "O gerador de PDF existente define o layout e o conteúdo "
    "do relatório. Os campos adicionais acima aparecem na interface, "
    "mas só são enviados ao gerador se a interface dele os suportar."
)

st.markdown("---")


# ------------------------------------------------
# GENERATE PDF REPORT
# ------------------------------------------------

st.subheader("📄 Gerar PDF Executivo")

st.write(
    "Gere um PDF para download com o ExecutiveReportBuilder "
    "existente."
)

if st.button(
    "📄 Gerar Relatório Executivo",
    type="primary",
    use_container_width=True
):

    try:

        builder = ExecutiveReportBuilder()

        with st.spinner("Gerando o relatório executivo..."):

            filename = builder.generate(
                filename=report_filename,
                dataset_summary=dataset_summary,
                health_score=health,
                automl_result=automl_result,
                recommendations=final_recommendations,
                anomaly_summary=final_anomaly_summary
            )

        if not filename:
            st.error(
                "O gerador de relatórios não retornou um caminho de arquivo."
            )

        elif not os.path.isfile(filename):
            st.error(
                "O gerador de relatórios retornou um caminho, "
                "mas o arquivo não foi encontrado."
            )

        else:

            with open(filename, "rb") as report_file:
                pdf_bytes = report_file.read()

            st.session_state["executive_report_pdf"] = pdf_bytes
            st.session_state["executive_report_filename"] = (
                os.path.basename(filename)
            )

            st.success(
                "Relatório executivo gerado com sucesso."
            )

    except Exception as error:

        st.error(
            f"Falha ao gerar o relatório: {error}"
        )

if "executive_report_pdf" in st.session_state:

    st.download_button(
        "⬇️ Baixar PDF do Relatório Executivo",
        data=st.session_state["executive_report_pdf"],
        file_name=st.session_state.get(
            "executive_report_filename",
            "Executive_Report.pdf"
        ),
        mime="application/pdf",
        use_container_width=True
    )


# ------------------------------------------------
# AI INSIGHT
# ------------------------------------------------

st.markdown("---")

ai_insight(
    "Um relatório executivo ajuda as partes interessadas a revisar "
    "a qualidade dos dados, os riscos potenciais e os próximos "
    "passos recomendados. O desempenho dos modelos e as anomalias "
    "só devem ser reportados quando houver resultados reais de "
    "análise."
)


# ------------------------------------------------
# PAGE NAVIGATION
# ------------------------------------------------

st.markdown("---")

st.subheader("🧭 Continue Explorando o NexDecision AI")

prev_col, home_col, next_col = st.columns(3)

with prev_col:
    if st.button(
        "⬅️ Detecção de Anomalias com IA",
        use_container_width=True
    ):
        st.switch_page("pages/17_AI_Anomaly_Detection.py")

with home_col:
    if st.button(
        "🏠 Início",
        use_container_width=True
    ):
        st.switch_page("pages/0_Home.py")



# ------------------------------------------------
# FOOTER
# ------------------------------------------------

page_footer()
