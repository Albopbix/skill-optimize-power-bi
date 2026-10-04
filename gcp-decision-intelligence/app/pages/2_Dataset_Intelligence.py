import streamlit as st
import pandas as pd
import textwrap

from src.ui.layout import (
    page_header,
    ai_insight,
    page_footer
)

from src.dataset_intelligence.dataset_detector import (
    DatasetDetector
)

from src.dataset_intelligence.column_mapper import (
    ColumnMapper
)

from src.dataset_intelligence.recommendation_engine import (
    RecommendationEngine
)

from src.dataset_intelligence.quality_engine import (
    QualityEngine
)

from src.dataset_intelligence.insight_engine import (
    InsightEngine
)


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Inteligência do Dataset | Nex Decision AI",
    page_icon="🧠",
    layout="wide"
)


# ============================================================
# CUSTOM UI
# ============================================================

st.markdown(
    textwrap.dedent(
        """
        <style>

        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 2rem;
        }

        .intel-hero {
            padding: 28px 30px;
            border-radius: 18px;
            background: linear-gradient(
                135deg,
                rgba(37,99,235,0.16),
                rgba(124,58,237,0.12)
            );
            border: 1px solid rgba(148,163,184,0.18);
            margin-bottom: 24px;
        }

        .intel-title {
            font-size: 32px;
            font-weight: 800;
            margin-bottom: 8px;
        }

        .intel-subtitle {
            font-size: 16px;
            color: #94a3b8;
            line-height: 1.6;
        }

        .status-card {
            padding: 18px 20px;
            border-radius: 14px;
            border: 1px solid rgba(148,163,184,0.15);
            background: rgba(15,23,42,0.45);
            min-height: 120px;
        }

        .status-icon {
            font-size: 25px;
            margin-bottom: 8px;
        }

        .status-title {
            font-size: 14px;
            color: #94a3b8;
            margin-bottom: 5px;
        }

        .status-value {
            font-size: 25px;
            font-weight: 800;
        }

        .section-title {
            font-size: 21px;
            font-weight: 750;
            margin-top: 20px;
            margin-bottom: 14px;
        }

        .quality-card {
            padding: 22px;
            border-radius: 16px;
            border: 1px solid rgba(148,163,184,0.15);
            background: rgba(15,23,42,0.42);
            margin-bottom: 15px;
        }

        .quality-score {
            font-size: 38px;
            font-weight: 850;
        }

        .quality-label {
            color: #94a3b8;
            font-size: 14px;
        }

        .feature-card {
            padding: 18px;
            border-radius: 14px;
            border: 1px solid rgba(148,163,184,0.14);
            background: rgba(15,23,42,0.38);
            min-height: 145px;
        }

        .feature-icon {
            font-size: 27px;
            margin-bottom: 8px;
        }

        .feature-title {
            font-size: 16px;
            font-weight: 700;
            margin-bottom: 6px;
        }

        .feature-text {
            color: #94a3b8;
            font-size: 13px;
            line-height: 1.5;
        }

        .file-badge {
            display: inline-block;
            padding: 7px 13px;
            border-radius: 18px;
            background: rgba(59,130,246,0.12);
            border: 1px solid rgba(59,130,246,0.25);
            color: #bfdbfe;
            font-size: 13px;
            margin-top: 8px;
        }

        .insight-card {
            padding: 15px 18px;
            border-radius: 12px;
            background: rgba(30,41,59,0.5);
            border-left: 4px solid #6366f1;
            margin-bottom: 10px;
        }

        .mapping-card {
            padding: 12px 16px;
            border-radius: 10px;
            background: rgba(30,41,59,0.42);
            border: 1px solid rgba(148,163,184,0.12);
            margin-bottom: 8px;
        }

        .nav-note {
            text-align: center;
            color: #64748b;
            font-size: 12px;
            padding-top: 8px;
        }

        </style>
        """
    ),
    unsafe_allow_html=True
)


# ============================================================
# HEADER
# ============================================================

page_header(
    "🧠 Inteligência do Dataset",
    "Transforme dados brutos em um perfil de inteligência estruturado antes de predições, automações e decisões de negócio."
)


# ============================================================
# CHECK DATASET
# ============================================================

if "dataset" not in st.session_state:

    st.warning(
        "📂 Nenhum dataset foi enviado ainda."
    )

    st.info(
        "Vá em **Enviar Dataset** e envie um dataset de negócio primeiro."
    )

    if st.button(
        "📂 Ir para Enviar Dataset",
        width="content"
    ):
        st.switch_page("pages/1_Upload_Dataset.py")

    st.stop()


# ============================================================
# LOAD DATASET
# ============================================================

df = st.session_state["dataset"]

filename = st.session_state.get(
    "filename",
    "Dataset enviado"
)


# ============================================================
# BASIC VALIDATION
# ============================================================

if df is None or df.empty:

    st.error(
        "❌ O dataset está vazio ou indisponível."
    )

    if st.button(
        "📂 Voltar para Enviar Dataset"
    ):
        st.switch_page("pages/1_Upload_Dataset.py")

    st.stop()


# ============================================================
# DATASET HERO
# ============================================================

st.markdown(
    textwrap.dedent(
        f"""
        <div class="intel-hero">
            <div class="intel-title">🔎 Perfil de Inteligência</div>
            <div class="intel-subtitle">
                O Nex Decision AI está examinando a estrutura, a qualidade,
                a compatibilidade e o potencial de negócio do seu dataset.
            </div>
            <div class="file-badge">📄 {filename}</div>
        </div>
        """
    ),
    unsafe_allow_html=True
)


# ============================================================
# QUICK DATA HEALTH
# ============================================================

total_rows = len(df)
total_columns = len(df.columns)
missing_values = int(df.isnull().sum().sum())
duplicate_rows = int(df.duplicated().sum())

numeric_columns = len(
    df.select_dtypes(include="number").columns
)

categorical_columns = len(
    df.select_dtypes(include=["object", "category", "bool"]).columns
)

date_columns = len(
    df.select_dtypes(include=["datetime", "datetimetz"]).columns
)


st.markdown(
    '<div class="section-title">📊 Saúde do Dataset</div>',
    unsafe_allow_html=True
)

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(
        textwrap.dedent(
            f"""
            <div class="status-card">
                <div class="status-icon">📄</div>
                <div class="status-title">Registros</div>
                <div class="status-value">{total_rows:,}</div>
            </div>
            """
        ),
        unsafe_allow_html=True
    )

with c2:
    st.markdown(
        textwrap.dedent(
            f"""
            <div class="status-card">
                <div class="status-icon">🗂️</div>
                <div class="status-title">Variáveis</div>
                <div class="status-value">{total_columns}</div>
            </div>
            """
        ),
        unsafe_allow_html=True
    )

with c3:
    st.markdown(
        textwrap.dedent(
            f"""
            <div class="status-card">
                <div class="status-icon">⚠️</div>
                <div class="status-title">Valores Ausentes</div>
                <div class="status-value">{missing_values:,}</div>
            </div>
            """
        ),
        unsafe_allow_html=True
    )

with c4:
    st.markdown(
        textwrap.dedent(
            f"""
            <div class="status-card">
                <div class="status-icon">🔁</div>
                <div class="status-title">Linhas Duplicadas</div>
                <div class="status-value">{duplicate_rows:,}</div>
            </div>
            """
        ),
        unsafe_allow_html=True
    )


# ============================================================
# DATASET PROFILE
# ============================================================

st.markdown(
    '<div class="section-title">🧬 Perfil do Dataset</div>',
    unsafe_allow_html=True
)

p1, p2, p3 = st.columns(3)

with p1:
    st.markdown(
        textwrap.dedent(
            f"""
            <div class="feature-card">
                <div class="feature-icon">🔢</div>
                <div class="feature-title">Variáveis Numéricas</div>
                <div class="feature-text">
                    {numeric_columns} colunas numéricas detectadas.
                    Adequadas para análise estatística, previsões
                    e machine learning.
                </div>
            </div>
            """
        ),
        unsafe_allow_html=True
    )

with p2:
    st.markdown(
        textwrap.dedent(
            f"""
            <div class="feature-card">
                <div class="feature-icon">🏷️</div>
                <div class="feature-title">Variáveis Categóricas</div>
                <div class="feature-text">
                    {categorical_columns} colunas categóricas detectadas.
                    Úteis para segmentação, classificação e
                    agrupamentos de negócio.
                </div>
            </div>
            """
        ),
        unsafe_allow_html=True
    )

with p3:
    st.markdown(
        textwrap.dedent(
            f"""
            <div class="feature-card">
                <div class="feature-icon">📅</div>
                <div class="feature-title">Variáveis de Data</div>
                <div class="feature-text">
                    {date_columns} colunas de data/hora detectadas.
                    Úteis para análise de tendências e previsões.
                </div>
            </div>
            """
        ),
        unsafe_allow_html=True
    )


# ============================================================
# ANALYSIS ENGINES
# ============================================================

try:

    with st.spinner(
        "🧠 O Nex Decision AI está montando seu perfil de inteligência..."
    ):

        # --------------------------------------------------------
        # DATASET DETECTOR
        # --------------------------------------------------------

        detector = DatasetDetector(df)

        report = detector.analyze_dataset()

        dataset_type, confidence = (
            detector.detect_dataset_type()
        )

        compatibility, reason = (
            detector.check_compatibility()
        )

        # --------------------------------------------------------
        # COLUMN MAPPER
        # --------------------------------------------------------

        mapper = ColumnMapper(
            df.columns
        )

        mapped_columns = (
            mapper.map_columns()
        )

        # --------------------------------------------------------
        # RECOMMENDATION ENGINE
        # --------------------------------------------------------

        recommendation_engine = (
            RecommendationEngine(
                dataset_type
            )
        )

        recommendations = (
            recommendation_engine.recommend()
        )

        # --------------------------------------------------------
        # QUALITY ENGINE
        # --------------------------------------------------------

        quality_engine = QualityEngine(
            df
        )

        quality_report = (
            quality_engine.generate_quality_report()
        )

        # --------------------------------------------------------
        # INSIGHT ENGINE
        # --------------------------------------------------------

        insight_engine = InsightEngine(
            dataset_type,
            quality_report,
            compatibility
        )

        insights = (
            insight_engine.generate_insights()
        )

    st.success(
        "✅ Análise de inteligência do dataset concluída."
    )

except Exception as e:

    st.error(
        "❌ O Nex Decision AI não conseguiu concluir a análise do dataset."
    )

    st.info(
        "O dataset continua salvo. Você pode voltar em Enviar "
        "Dataset e tentar outro arquivo."
    )

    with st.expander("Detalhes técnicos"):
        st.write(str(e))

    st.stop()


# ============================================================
# AI DATASET CLASSIFICATION 2.0
# ============================================================

st.markdown(
    '<div class="section-title">🧠 Classificação do Dataset por IA</div>',
    unsafe_allow_html=True
)


# ------------------------------------------------------------
# INTELLIGENCE FUNCTIONS
# ------------------------------------------------------------

REPORT_LABELS_PT = {
    "Rows": "Linhas",
    "Columns": "Colunas",
    "Missing Values": "Valores Ausentes",
    "Duplicate Rows": "Linhas Duplicadas",
    "Column Names": "Nomes das Colunas",
    "Quality Score": "Score de Qualidade",
    "Grade": "Nota",
    "Missing %": "% Ausentes",
    "Duplicate %": "% Duplicados",
}


def translate_report_keys(report):

    """Traduz as chaves dos relatórios dos motores apenas para exibição."""

    return {
        REPORT_LABELS_PT.get(key, key): value
        for key, value in report.items()
    }


def detect_dataset_domain(df):
    """
    Lightweight explainable domain detection based on
    column-name patterns.
    """

    columns = [
        str(col).lower().replace("_", " ").replace("-", " ")
        for col in df.columns
    ]

    domain_rules = {
        "Análise de Clientes": [
            "customer",
            "client",
            "churn",
            "age",
            "gender",
            "income",
            "customer id"
        ],

        "Vendas e Varejo": [
            "sales",
            "revenue",
            "product",
            "price",
            "quantity",
            "order",
            "invoice",
            "discount"
        ],

        "Finanças": [
            "loan",
            "credit",
            "transaction",
            "balance",
            "interest",
            "payment",
            "financial"
        ],

        "Recursos Humanos": [
            "employee",
            "salary",
            "department",
            "job role",
            "attrition",
            "experience",
            "hire"
        ],

        "Saúde": [
            "patient",
            "diagnosis",
            "disease",
            "hospital",
            "medical",
            "blood",
            "treatment"
        ],

        "Marketing": [
            "campaign",
            "conversion",
            "click",
            "impression",
            "marketing",
            "lead",
            "engagement"
        ],

        "Educação": [
            "student",
            "marks",
            "grade",
            "attendance",
            "course",
            "exam",
            "college"
        ],

        "Operações": [
            "inventory",
            "supply",
            "warehouse",
            "delivery",
            "shipment",
            "stock",
            "logistics"
        ]
    }

    scores = {}

    for domain, keywords in domain_rules.items():

        score = 0

        for column in columns:

            for keyword in keywords:

                if keyword in column:
                    score += 1

        scores[domain] = score

    if not scores or max(scores.values()) == 0:

        return "Dataset de Negócio Geral", 0

    best_domain = max(
        scores,
        key=scores.get
    )

    max_score = scores[best_domain]

    confidence = min(
        95,
        int(
            50 +
            (max_score * 8)
        )
    )

    return best_domain, confidence


def detect_ml_use_cases(df):

    use_cases = []

    numeric_cols = df.select_dtypes(
        include="number"
    ).columns.tolist()

    categorical_cols = df.select_dtypes(
        include=[
            "object",
            "category",
            "bool"
        ]
    ).columns.tolist()

    date_cols = df.select_dtypes(
        include=[
            "datetime",
            "datetimetz"
        ]
    ).columns.tolist()

    # Regression potential
    for col in numeric_cols:

        unique_ratio = (
            df[col].nunique() /
            max(len(df), 1)
        )

        if unique_ratio > 0.05:

            use_cases.append(
                "📈 Regressão / Predição Numérica"
            )
            break

    # Classification potential
    for col in categorical_cols:

        unique_count = df[col].nunique()

        if 2 <= unique_count <= 20:

            use_cases.append(
                "🏷️ Classificação"
            )
            break

    # Time series
    if date_cols and numeric_cols:

        use_cases.append(
            "⏳ Previsão de Séries Temporais"
        )

    # Clustering
    if len(numeric_cols) >= 3:

        use_cases.append(
            "🎯 Segmentação de Clientes / Entidades"
        )

    # Anomaly detection
    if len(numeric_cols) >= 2:

        use_cases.append(
            "🚨 Detecção de Anomalias"
        )

    if not use_cases:

        use_cases.append(
            "📊 Analytics Descritivo de Negócio"
        )

    return list(dict.fromkeys(use_cases))


def find_target_candidates(df):

    candidates = []

    for col in df.columns:

        series = df[col]

        unique_count = series.nunique(
            dropna=True
        )

        if unique_count <= 1:
            continue

        unique_ratio = (
            unique_count /
            max(len(df), 1)
        )

        # Ignore obvious IDs
        col_lower = str(col).lower()

        if (
            col_lower.endswith("id")
            or col_lower.startswith("id")
            or "identifier" in col_lower
        ):
            continue

        # Classification candidate
        if (
            series.dtype == "object"
            or str(series.dtype) == "category"
            or series.dtype == "bool"
        ):

            if 2 <= unique_count <= 20:

                candidates.append(
                    (
                        col,
                        "Alvo de classificação"
                    )
                )

        # Regression candidate
        elif pd.api.types.is_numeric_dtype(
            series
        ):

            if unique_ratio < 0.95:

                candidates.append(
                    (
                        col,
                        "Alvo de regressão"
                    )
                )

    return candidates[:8]


def calculate_complexity_score(df):

    score = 0

    rows = len(df)
    columns = len(df.columns)

    numeric_count = len(
        df.select_dtypes(
            include="number"
        ).columns
    )

    categorical_count = len(
        df.select_dtypes(
            include=[
                "object",
                "category"
            ]
        ).columns
    )

    missing_ratio = (
        df.isnull().sum().sum()
        /
        max(
            df.size,
            1
        )
    )

    # Dataset size
    if rows > 10000:
        score += 20
    elif rows > 1000:
        score += 12
    else:
        score += 6

    # Feature complexity
    if columns > 30:
        score += 20
    elif columns > 15:
        score += 12
    else:
        score += 6

    # Numeric complexity
    if numeric_count >= 10:
        score += 15
    elif numeric_count >= 5:
        score += 10

    # Categorical complexity
    if categorical_count >= 8:
        score += 15
    elif categorical_count >= 4:
        score += 8

    # Missingness
    if missing_ratio > 0.20:
        score += 20
    elif missing_ratio > 0.05:
        score += 10

    return min(score, 100)


def calculate_ml_readiness(df):

    score = 100

    missing_ratio = (
        df.isnull().sum().sum()
        /
        max(df.size, 1)
    )

    duplicate_ratio = (
        df.duplicated().sum()
        /
        max(len(df), 1)
    )

    if missing_ratio > 0.20:
        score -= 25
    elif missing_ratio > 0.10:
        score -= 15
    elif missing_ratio > 0.05:
        score -= 8

    if duplicate_ratio > 0.20:
        score -= 20
    elif duplicate_ratio > 0.05:
        score -= 10

    numeric_count = len(
        df.select_dtypes(
            include="number"
        ).columns
    )

    if numeric_count == 0:
        score -= 25
    elif numeric_count < 2:
        score -= 10

    if len(df) < 100:
        score -= 15
    elif len(df) < 500:
        score -= 5

    return max(
        0,
        min(score, 100)
    )


def detect_risks(df):

    risks = []

    missing_ratio = (
        df.isnull().sum().sum()
        /
        max(df.size, 1)
    )

    duplicate_count = df.duplicated().sum()

    if missing_ratio > 0.20:

        risks.append(
            "Alta proporção de dados ausentes detectada."
        )

    elif missing_ratio > 0.05:

        risks.append(
            "Proporção moderada de dados ausentes detectada."
        )

    if duplicate_count > 0:

        risks.append(
            f"{duplicate_count:,} linhas duplicadas detectadas."
        )

    for col in df.columns:

        unique_count = df[col].nunique(
            dropna=True
        )

        if (
            unique_count == 1
            and len(df) > 1
        ):

            risks.append(
                f"Coluna constante detectada: {col}"
            )

        if (
            unique_count > 0
            and unique_count == len(df)
            and (
                str(col).lower().endswith("id")
                or "identifier"
                in str(col).lower()
            )
        ):

            risks.append(
                f"Possível coluna identificadora: {col}"
            )

    return risks[:8]


# ------------------------------------------------------------
# RUN INTELLIGENCE
# ------------------------------------------------------------

domain, domain_confidence = (
    detect_dataset_domain(df)
)

ml_use_cases = detect_ml_use_cases(df)

target_candidates = find_target_candidates(df)

complexity_score = (
    calculate_complexity_score(df)
)

ml_readiness = (
    calculate_ml_readiness(df)
)

risks = detect_risks(df)


# ============================================================
# CLASSIFICATION OVERVIEW
# ============================================================

c1, c2, c3 = st.columns(3)

with c1:

    st.markdown(
        textwrap.dedent(
            f"""
            <div class="quality-card">
                <div class="quality-label">
                    TIPO DE DATASET (IA)
                </div>
                <div class="quality-score">
                    {dataset_type}
                </div>
                <div class="quality-label">
                    Confiança do motor: {confidence}%
                </div>
            </div>
            """
        ),
        unsafe_allow_html=True
    )

with c2:

    st.markdown(
        textwrap.dedent(
            f"""
            <div class="quality-card">
                <div class="quality-label">
                    SETOR DE NEGÓCIO
                </div>
                <div class="quality-score">
                    {domain}
                </div>
                <div class="quality-label">
                    Confiança do padrão: {domain_confidence}%
                </div>
            </div>
            """
        ),
        unsafe_allow_html=True
    )

with c3:

    st.markdown(
        textwrap.dedent(
            f"""
            <div class="quality-card">
                <div class="quality-label">
                    PRONTIDÃO PARA ML
                </div>
                <div class="quality-score">
                    {ml_readiness}/100
                </div>
                <div class="quality-label">
                    Com base na estrutura e na qualidade dos dados
                </div>
            </div>
            """
        ),
        unsafe_allow_html=True
    )


# ============================================================
# DATASET COMPLEXITY
# ============================================================

st.markdown(
    '<div class="section-title">⚙️ Complexidade do Dataset</div>',
    unsafe_allow_html=True
)

complexity_label = "Baixa"

if complexity_score >= 70:
    complexity_label = "Alta"
elif complexity_score >= 40:
    complexity_label = "Moderada"


st.progress(
    complexity_score / 100
)

st.caption(
    f"Score de complexidade: {complexity_score}/100 "
    f"— complexidade {complexity_label}"
)


# ============================================================
# MACHINE LEARNING OPPORTUNITIES
# ============================================================

st.markdown(
    '<div class="section-title">🚀 Oportunidades de IA Detectadas</div>',
    unsafe_allow_html=True
)

cols = st.columns(
    min(len(ml_use_cases), 3)
)

for index, use_case in enumerate(
    ml_use_cases
):

    with cols[index % len(cols)]:

        st.markdown(
            textwrap.dedent(
                f"""
                <div class="feature-card">
                    <div class="feature-icon">🤖</div>
                    <div class="feature-title">
                        {use_case}
                    </div>
                    <div class="feature-text">
                        Possível fluxo analítico detectado
                        a partir da estrutura do seu dataset.
                    </div>
                </div>
                """
            ),
            unsafe_allow_html=True
        )


# ============================================================
# TARGET INTELLIGENCE
# ============================================================

st.markdown(
    '<div class="section-title">🎯 Inteligência de Coluna-Alvo</div>',
    unsafe_allow_html=True
)

if target_candidates:

    st.write(
        "Possíveis alvos de predição detectados:"
    )

    target_data = pd.DataFrame(
        target_candidates,
        columns=[
            "Coluna",
            "Papel provável"
        ]
    )

    st.dataframe(
        target_data,
        width="stretch",
        hide_index=True
    )

else:

    st.info(
        "Nenhum alvo de predição óbvio foi detectado. "
        "O dataset pode ser mais adequado para clusterização, "
        "analytics descritivo ou previsões."
    )


# ============================================================
# RISK DETECTION
# ============================================================

st.markdown(
    '<div class="section-title">🛡️ Detecção de Riscos do Dataset</div>',
    unsafe_allow_html=True
)

if risks:

    for risk in risks:

        st.warning(
            f"⚠️ {risk}"
        )

else:

    st.success(
        "✅ Nenhum risco estrutural relevante detectado."
    )


# ============================================================
# WHY THIS CLASSIFICATION?
# ============================================================

st.markdown(
    '<div class="section-title">🔎 Por que o Nex Decision AI classificou assim</div>',
    unsafe_allow_html=True
)

st.info(
    f"""
    **Classificação do dataset:** {dataset_type}

    **Setor de negócio detectado:** {domain}

    **Possíveis fluxos de IA:** {", ".join(ml_use_cases)}

    **Alvos de predição detectados:** {len(target_candidates)}

    **Prontidão para ML:** {ml_readiness}/100

    A classificação combina o motor de Inteligência do Dataset
    com análise de estrutura, tipos de coluna e padrões de nomes.
    """
)


# ============================================================
# COMPATIBILITY
# ============================================================

st.markdown(
    '<div class="section-title">🔗 Compatibilidade com a Plataforma</div>',
    unsafe_allow_html=True
)

if str(compatibility).lower() == "compatible":

    st.success(
        "✅ O dataset é compatível com o Nex Decision AI."
    )

else:

    st.warning(
        "⚠️ O dataset não é totalmente compatível com o Nex Decision AI."
    )

st.info(reason)

# ============================================================
# DATASET ANALYSIS
# ============================================================

st.markdown(
    '<div class="section-title">🔍 Análise do Dataset</div>',
    unsafe_allow_html=True
)

with st.expander(
    "Ver análise detalhada do dataset",
    expanded=False
):

    if isinstance(report, dict):
        st.json(translate_report_keys(report))
    else:
        st.write(report)


# ============================================================
# COLUMN INTELLIGENCE
# ============================================================

st.markdown(
    '<div class="section-title">🗂️ Inteligência de Colunas</div>',
    unsafe_allow_html=True
)

st.caption(
    "O Nex Decision AI mapeia suas colunas para conceitos de negócio reutilizáveis."
)

with st.expander(
    "Ver mapeamento de colunas detectado",
    expanded=True
):

    if isinstance(mapped_columns, dict):

        for key, value in mapped_columns.items():

            st.markdown(
                textwrap.dedent(
                    f"""
                    <div class="mapping-card">
                        <strong>{key}</strong>
                        <br>
                        <span style="color:#94a3b8;">
                            {value}
                        </span>
                    </div>
                    """
                ),
                unsafe_allow_html=True
            )

    else:

        st.write(mapped_columns)


# ============================================================
# DATA QUALITY
# ============================================================

st.markdown(
    '<div class="section-title">📈 Inteligência de Qualidade dos Dados</div>',
    unsafe_allow_html=True
)

try:

    quality_score = quality_report.get(
        "Quality Score",
        "Desconhecido"
    )

    grade = quality_report.get(
        "Grade",
        "Desconhecido"
    )

except Exception:

    quality_score = "Desconhecido"
    grade = "Desconhecido"


q1, q2 = st.columns(2)

with q1:

    st.markdown(
        textwrap.dedent(
            f"""
            <div class="quality-card">
                <div class="quality-label">
                    SCORE GERAL DE QUALIDADE
                </div>
                <div class="quality-score">
                    {quality_score}
                </div>
            </div>
            """
        ),
        unsafe_allow_html=True
    )

with q2:

    st.markdown(
        textwrap.dedent(
            f"""
            <div class="quality-card">
                <div class="quality-label">
                    NOTA DE QUALIDADE DOS DADOS
                </div>
                <div class="quality-score">
                    {grade}
                </div>
            </div>
            """
        ),
        unsafe_allow_html=True
    )


with st.expander(
    "📋 Ver relatório de qualidade completo"
):

    if isinstance(quality_report, dict):
        st.json(translate_report_keys(quality_report))
    else:
        st.write(quality_report)


# ============================================================
# AI RECOMMENDATIONS
# ============================================================

st.markdown(
    '<div class="section-title">🤖 Soluções de IA Recomendadas</div>',
    unsafe_allow_html=True
)

if recommendations:

    for item in recommendations:

        st.markdown(
            textwrap.dedent(
                f"""
                <div class="insight-card">
                    💡 {item}
                </div>
                """
            ),
            unsafe_allow_html=True
        )

else:

    st.info(
        "Nenhuma recomendação de IA específica foi gerada."
    )


# ============================================================
# BUSINESS INSIGHTS
# ============================================================

st.markdown(
    '<div class="section-title">💡 Insights de Negócio da IA</div>',
    unsafe_allow_html=True
)

if insights:

    for insight in insights:

        st.markdown(
            textwrap.dedent(
                f"""
                <div class="insight-card">
                    💡 {insight}
                </div>
                """
            ),
            unsafe_allow_html=True
        )

else:

    st.info(
        "Nenhum insight de negócio adicional foi gerado."
    )


# ============================================================
# DATASET PREVIEW
# ============================================================

st.markdown(
    '<div class="section-title">📋 Prévia dos Dados</div>',
    unsafe_allow_html=True
)

with st.expander(
    "Ver os 20 primeiros registros"
):

    st.dataframe(
        df.head(20),
        width="stretch",
        hide_index=True
    )


# ============================================================
# AI INSIGHT
# ============================================================

ai_insight(
    "Uma boa decisão começa pelo entendimento dos dados. O Nex "
    "Decision AI traçou o perfil do seu dataset antes de seguir "
    "para os fluxos de predição, automação e decisão de negócio."
)


# ============================================================
# NAVIGATION
# ============================================================

st.divider()

prev_col, center_col, next_col = st.columns(
    [1, 2, 1]
)

with prev_col:

    if st.button(
        "⬅️ Anterior",
        width="stretch"
    ):
        st.switch_page(
            "pages/1_Upload_Dataset.py"
        )

with center_col:

    st.markdown(
        '<div class="nav-note">Etapa 2 do fluxo de inteligência</div>',
        unsafe_allow_html=True
    )

with next_col:

    if st.button(
        "Próximo ➡️",
        width="stretch"
    ):
        st.switch_page(
            "pages/3_AI_Business_Copilot.py"
        )


# ============================================================
# FOOTER
# ============================================================

page_footer()