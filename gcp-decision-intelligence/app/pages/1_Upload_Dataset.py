import streamlit as st
import pandas as pd
import textwrap

from src.ui.layout import page_header, ai_insight, page_footer


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Enviar Dataset | Nex Decision AI",
    page_icon="📂",
    layout="wide"
)


# ============================================================
# CUSTOM PAGE STYLE
# ============================================================

st.markdown(
    textwrap.dedent("""
    <style>

    .block-container {
        max-width: 1280px;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    .upload-hero {
        padding: 28px 32px;
        border-radius: 20px;
        background: linear-gradient(
            135deg,
            rgba(49, 51, 63, 0.95),
            rgba(31, 41, 55, 0.92)
        );
        border: 1px solid rgba(255,255,255,0.08);
        margin-bottom: 25px;
    }

    .upload-title {
        font-size: 30px;
        font-weight: 750;
        margin-bottom: 8px;
    }

    .upload-subtitle {
        font-size: 15px;
        opacity: 0.72;
        line-height: 1.6;
        max-width: 900px;
    }

    .section-title {
        font-size: 22px;
        font-weight: 700;
        margin-top: 18px;
        margin-bottom: 14px;
    }

    .info-card {
        padding: 18px;
        border-radius: 15px;
        border: 1px solid rgba(128,128,128,0.20);
        min-height: 105px;
    }

    .info-icon {
        font-size: 26px;
    }

    .info-title {
        font-size: 15px;
        font-weight: 700;
        margin-top: 6px;
    }

    .info-text {
        font-size: 12px;
        opacity: 0.65;
        margin-top: 4px;
        line-height: 1.5;
    }

    .upload-zone {
        padding: 24px;
        border-radius: 18px;
        border: 1px solid rgba(100,150,255,0.25);
        background: rgba(70,100,180,0.06);
        margin-top: 10px;
        margin-bottom: 20px;
        line-height: 2;
    }

    .format-title {
        font-size: 16px;
        font-weight: 700;
        margin-bottom: 8px;
    }

    .format-item {
        display: inline-block;
        padding: 6px 12px;
        margin: 4px;
        border-radius: 10px;
        border: 1px solid rgba(128,128,128,0.20);
        font-size: 13px;
    }

    .status-card {
        padding: 18px;
        border-radius: 15px;
        border: 1px solid rgba(128,128,128,0.18);
        margin-top: 15px;
    }

    .status-title {
        font-size: 15px;
        font-weight: 700;
    }

    .status-text {
        font-size: 13px;
        opacity: 0.72;
        margin-top: 5px;
    }

    </style>
    """),
    unsafe_allow_html=True
)


# ============================================================
# DATASET LOADER
# ============================================================

@st.cache_data
def load_dataset(file_bytes, filename):
    """
    Load supported business/data-science dataset formats.
    """

    try:

        from io import BytesIO, StringIO

        extension = filename.lower().split(".")[-1]

        # ----------------------------------------------------
        # CSV
        # ----------------------------------------------------

        if extension == "csv":

            return pd.read_csv(
                BytesIO(file_bytes)
            )

        # ----------------------------------------------------
        # EXCEL
        # ----------------------------------------------------

        elif extension in ["xlsx", "xls"]:

            return pd.read_excel(
                BytesIO(file_bytes)
            )

        # ----------------------------------------------------
        # JSON
        # ----------------------------------------------------

        elif extension == "json":

            return pd.read_json(
                BytesIO(file_bytes)
            )

        # ----------------------------------------------------
        # TSV
        # ----------------------------------------------------

        elif extension == "tsv":

            return pd.read_csv(
                BytesIO(file_bytes),
                sep="\t"
            )

        # ----------------------------------------------------
        # TXT
        # ----------------------------------------------------

        elif extension == "txt":

            return pd.read_csv(
                StringIO(
                    file_bytes.decode("utf-8")
                )
            )

        # ----------------------------------------------------
        # PARQUET
        # ----------------------------------------------------

        elif extension == "parquet":

            return pd.read_parquet(
                BytesIO(file_bytes)
            )

        return None

    except Exception:
        return None


# ============================================================
# PAGE HEADER
# ============================================================




# ============================================================
# HERO
# ============================================================

st.markdown(
    textwrap.dedent("""
    <div class="upload-hero">
        <div class="upload-title">
            📂 Traga os dados do seu negócio para o Nex Decision AI
        </div>
        <div class="upload-subtitle">
            Envie dados estruturados do negócio e prepare-os para
            inteligência de dados, machine learning, previsões,
            detecção de anomalias e análise de decisão.
        </div>
    </div>
    """),
    unsafe_allow_html=True
)


# ============================================================
# WHAT HAPPENS AFTER UPLOAD
# ============================================================

st.markdown(
    '<div class="section-title">🚀 O que o Nex Decision AI vai analisar</div>',
    unsafe_allow_html=True
)

analysis_features = [
    (
        "📊",
        "Estatísticas do Dataset",
        "Linhas, colunas e medidas essenciais do dataset."
    ),
    (
        "🔎",
        "Estrutura dos Dados",
        "Identifique campos numéricos, categóricos e de data."
    ),
    (
        "🧹",
        "Qualidade dos Dados",
        "Detecte valores ausentes e registros duplicados."
    ),
    (
        "🤖",
        "Oportunidades de IA",
        "Prepare o dataset para análises de machine learning."
    ),
]

feature_columns = st.columns(4)

for column, feature in zip(
    feature_columns,
    analysis_features
):

    icon, title, description = feature

    with column:

        st.markdown(
            textwrap.dedent(
                f"""
                <div class="info-card">
                    <div class="info-icon">{icon}</div>
                    <div class="info-title">{title}</div>
                    <div class="info-text">{description}</div>
                </div>
                """
            ),
            unsafe_allow_html=True
        )


st.markdown("---")


# ============================================================
# SUPPORTED FORMATS
# ============================================================

st.markdown(
    '<div class="section-title">📁 Formatos Suportados</div>',
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="format-list">
        <span class="format-item">📄 CSV</span>
        <span class="format-item">📊 Excel XLSX</span>
        <span class="format-item">📊 Excel XLS</span>
        <span class="format-item">🧾 JSON</span>
        <span class="format-item">📑 TSV</span>
        <span class="format-item">🗃️ Parquet</span>
        <span class="format-item">📋 TXT</span>
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# FILE UPLOADER
# ============================================================

st.markdown(
    '<div class="section-title">📤 Escolha seu Dataset</div>',
    unsafe_allow_html=True
)

uploaded_file = st.file_uploader(
    "Envie seu dataset",
    type=[
        "csv",
        "xlsx",
        "xls",
        "json",
        "tsv",
        "parquet",
        "txt"
    ],
    help=(
        "Formatos suportados: CSV, Excel, JSON, "
        "TSV, Parquet e TXT."
    )
)


# ============================================================
# PROCESS UPLOADED DATASET
# ============================================================

if uploaded_file is not None:

    try:

        with st.spinner(
            "Lendo e validando seu dataset..."
        ):

            file_bytes = uploaded_file.getvalue()

            df = load_dataset(
                file_bytes,
                uploaded_file.name
            )


        # ====================================================
        # VALIDATION
        # ====================================================

        if df is None:

            st.error(
                "❌ Não foi possível ler este arquivo. "
                "Verifique se o arquivo é válido e usa "
                "um formato tabular suportado."
            )

            st.stop()


        if df.empty:

            st.warning(
                "⚠️ O dataset enviado está vazio. Envie "
                "um dataset com registros."
            )

            st.stop()


        # ====================================================
        # STORE DATASET
        # ====================================================

        st.session_state["dataset"] = df

        st.session_state["filename"] = uploaded_file.name


        # ====================================================
        # SUCCESS
        # ====================================================

        st.success(
            f"✅ Dataset '{uploaded_file.name}' enviado com sucesso."
        )


        # ====================================================
        # FILE INFORMATION
        # ====================================================

        file_size_mb = len(file_bytes) / (1024 * 1024)

        extension = (
            uploaded_file.name
            .lower()
            .split(".")[-1]
            .upper()
        )

        st.markdown(
            textwrap.dedent(
                f"""
                <div class="status-card">
                    <div class="status-title">
                        📁 {uploaded_file.name}
                    </div>
                    <div class="status-text">
                        Formato: {extension}
                        &nbsp; • &nbsp;
                        Tamanho: {file_size_mb:.2f} MB
                        &nbsp; • &nbsp;
                        Status: Pronto para análise
                    </div>
                </div>
                """
            ),
            unsafe_allow_html=True
        )


        # ====================================================
        # DATASET OVERVIEW
        # ====================================================

        st.markdown(
            '<div class="section-title">📊 Visão Geral do Dataset</div>',
            unsafe_allow_html=True
        )

        missing_values = int(
            df.isnull().sum().sum()
        )

        duplicate_rows = int(
            df.duplicated().sum()
        )

        c1, c2, c3, c4 = st.columns(4)

        with c1:

            st.metric(
                "📄 Linhas",
                f"{len(df):,}"
            )

        with c2:

            st.metric(
                "📊 Colunas",
                f"{len(df.columns):,}"
            )

        with c3:

            st.metric(
                "⚠️ Valores Ausentes",
                f"{missing_values:,}"
            )

        with c4:

            st.metric(
                "🔁 Linhas Duplicadas",
                f"{duplicate_rows:,}"
            )


        st.divider()


        # ====================================================
        # DATASET PREVIEW
        # ====================================================

        st.markdown(
            '<div class="section-title">📋 Prévia do Dataset</div>',
            unsafe_allow_html=True
        )

        st.caption(
            "Exibindo os 10 primeiros registros para confirmar que o dataset foi carregado corretamente."
        )

        st.dataframe(
            df.head(10),
            width="stretch",
            hide_index=True
        )


        st.divider()


        # ====================================================
        # DATASET STRUCTURE
        # ====================================================

        st.markdown(
            '<div class="section-title">🔎 Estrutura do Dataset</div>',
            unsafe_allow_html=True
        )

        numeric_columns = len(
            df.select_dtypes(
                include="number"
            ).columns
        )

        categorical_columns = len(
            df.select_dtypes(
                include=["object", "category"]
            ).columns
        )

        datetime_columns = len(
            df.select_dtypes(
                include=["datetime"]
            ).columns
        )

        c1, c2, c3 = st.columns(3)

        with c1:

            st.metric(
                "🔢 Colunas Numéricas",
                numeric_columns
            )

        with c2:

            st.metric(
                "🔤 Colunas Categóricas",
                categorical_columns
            )

        with c3:

            st.metric(
                "📅 Colunas de Data",
                datetime_columns
            )


        # ====================================================
        # DATASET INFORMATION
        # ====================================================

        with st.expander(
            "📋 Ver informações detalhadas do dataset"
        ):

            st.write("### Nomes das Colunas")

            st.write(
                list(df.columns)
            )

            st.write("### Tipos de Dados")

            datatype_df = pd.DataFrame({
                "Coluna": df.columns,
                "Tipo de Dado": [
                    str(dtype)
                    for dtype in df.dtypes
                ]
            })

            st.dataframe(
                datatype_df,
                width="stretch",
                hide_index=True
            )


        # ====================================================
        # DATA QUALITY
        # ====================================================

        st.markdown(
            '<div class="section-title">🧹 Retrato da Qualidade dos Dados</div>',
            unsafe_allow_html=True
        )

        quality_columns = st.columns(3)

        with quality_columns[0]:

            if missing_values == 0:

                st.success(
                    "✅ Nenhum valor ausente detectado"
                )

            else:

                st.warning(
                    f"⚠️ {missing_values:,} valores ausentes detectados"
                )


        with quality_columns[1]:

            if duplicate_rows == 0:

                st.success(
                    "✅ Nenhuma linha duplicada detectada"
                )

            else:

                st.warning(
                    f"⚠️ {duplicate_rows:,} linhas duplicadas detectadas"
                )


        with quality_columns[2]:

            st.success(
                "✅ Estrutura do dataset detectada"
            )


        # ====================================================
        # READY STATUS
        # ====================================================

        st.markdown(
            textwrap.dedent("""
            <div class="status-card">
                <div class="status-title">
                    🚀 Dataset Pronto
                </div>
                <div class="status-text">
                    Seu dataset já está disponível no Nex Decision AI.
                    Continue em Inteligência do Dataset para descobrir
                    padrões, problemas de qualidade e oportunidades analíticas.
                </div>
            </div>
            """),
            unsafe_allow_html=True
        )


    except Exception as error:

        st.error(
            "❌ Não foi possível processar este dataset."
        )

        st.info(
            """
            Verifique se:

            • O arquivo está em um formato suportado  
            • O arquivo não está corrompido  
            • O dataset contém dados tabulares  

            Depois, tente enviar novamente.
            """
        )


# ============================================================
# AI INSIGHT
# ============================================================

ai_insight(
    "Dados de negócio limpos e bem estruturados ajudam o Nex Decision AI a gerar insights e predições mais confiáveis."
)


# ============================================================
# NAVIGATION
# ============================================================

st.markdown("---")

st.markdown(
    '<div class="section-title">🧭 Continue sua Análise</div>',
    unsafe_allow_html=True
)

n1, n2 = st.columns(2)

with n1:

    if st.button(
        "← Anterior · Início",
        width="stretch"
    ):

        st.switch_page(
            "pages/0_Home.py"
        )


with n2:

    if st.button(
        "Próximo · Inteligência do Dataset →",
        width="stretch"
    ):

        st.switch_page(
            "pages/2_Dataset_Intelligence.py"
        )


# ============================================================
# FOOTER
# ============================================================

page_footer()