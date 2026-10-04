import streamlit as st
import textwrap

from src.ui.theme import sidebar
from src.database.database import Database


# =====================================================
# PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="Nex Decision AI",
    page_icon="🤖",
    layout="wide"
)

sidebar()


# =====================================================
# CUSTOM HOME PAGE STYLE
# =====================================================

st.markdown(
    textwrap.dedent("""
    <style>
    .block-container {
        max-width: 1280px;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    .hero {
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

    .hero-title {
        font-size: 42px;
        font-weight: 750;
        margin-bottom: 5px;
    }

    .hero-subtitle {
        font-size: 17px;
        opacity: 0.75;
    }

    .hero-description {
        margin-top: 18px;
        font-size: 15px;
        line-height: 1.7;
        opacity: 0.85;
        max-width: 900px;
    }

    .section-title {
        font-size: 23px;
        font-weight: 700;
        margin-top: 15px;
        margin-bottom: 14px;
    }

    .feature-card {
        padding: 20px;
        border-radius: 16px;
        border: 1px solid rgba(128,128,128,0.20);
        min-height: 125px;
        margin-bottom: 14px;
        transition: 0.2s ease;
    }

    .feature-card:hover {
        border-color: rgba(128,128,128,0.45);
    }

    .feature-icon {
        font-size: 27px;
    }

    .feature-title {
        font-size: 17px;
        font-weight: 700;
        margin-top: 7px;
    }

    .feature-description {
        font-size: 13px;
        opacity: 0.68;
        margin-top: 5px;
        line-height: 1.5;
    }

    .domain-card {
        padding: 13px 15px;
        border-radius: 12px;
        border: 1px solid rgba(128,128,128,0.18);
        margin-bottom: 10px;
        font-size: 14px;
    }

    .workflow-card {
        padding: 20px;
        border-radius: 16px;
        border: 1px solid rgba(128,128,128,0.18);
        text-align: center;
        min-height: 110px;
    }

    .workflow-number {
        font-size: 13px;
        opacity: 0.55;
    }

    .workflow-icon {
        font-size: 27px;
        margin: 5px 0;
    }

    .workflow-title {
        font-weight: 650;
        font-size: 14px;
    }

    .ai-insight {
        padding: 22px;
        border-radius: 17px;
        border: 1px solid rgba(100,150,255,0.25);
        background: rgba(70,100,180,0.08);
    }

    .footer {
        text-align: center;
        opacity: 0.55;
        font-size: 12px;
        padding: 25px 0 5px 0;
    }
    </style>
    """),
    unsafe_allow_html=True
)


# =====================================================
# DATABASE
# =====================================================

database = Database()

uploads = database.get_uploads()
models = database.get_models()
predictions = database.get_predictions()


# =====================================================
# HERO SECTION
# =====================================================

st.markdown(
    textwrap.dedent("""
    <div class="hero">
        <div class="hero-title">🤖 Nex Decision AI</div>
        <div class="hero-subtitle">Plataforma Empresarial de Inteligência de Decisão</div>
        <div class="hero-description">
            Transforme dados brutos do negócio em decisões inteligentes com
            Machine Learning, Business Intelligence, 
            Previsões, Detecção de Anomalias e Analytics Executivo.
        </div>
    </div>
    """),
    unsafe_allow_html=True
)


# =====================================================
# PLATFORM STATUS
# =====================================================

st.markdown(
    '<div class="section-title">🚀 Status da Plataforma</div>',
    unsafe_allow_html=True
)

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric(
        "📂 Datasets",
        len(uploads)
    )

with c2:
    st.metric(
        "🤖 Modelos",
        len(models)
    )

with c3:
    st.metric(
        "🔮 Predições",
        len(predictions)
    )

with c4:
    st.metric(
        "⚡ Plataforma",
        "v2.2"
    )

st.markdown("---")


# =====================================================
# QUICK ACTIONS
# =====================================================

st.markdown(
    '<div class="section-title">⚡ Ações Rápidas</div>',
    unsafe_allow_html=True
)

q1, q2, q3, q4 = st.columns(4)

with q1:
    if st.button(
        "📂 Enviar Dataset",
        width="stretch"
    ):
        st.switch_page("pages/1_Upload_Dataset.py")

with q2:
    if st.button(
        "🔍 Inteligência do Dataset",
        width="stretch"
    ):
        st.switch_page("pages/2_Dataset_Intelligence.py")

with q3:
    if st.button(
        "⚙️ AutoML",
        width="stretch"
    ):
        st.switch_page("pages/5_AutoML.py")

with q4:
    if st.button(
        "📊 Painel Executivo",
        width="stretch"
    ):
        st.switch_page("pages/4_Executive_Dashboard.py")

st.markdown("---")


# =====================================================
# INTELLIGENCE CENTER
# =====================================================

st.markdown(
    '<div class="section-title">🧠 Central de Inteligência</div>',
    unsafe_allow_html=True
)

features = [
    (
        "📂",
        "Inteligência do Dataset",
        "Entenda qualidade, estrutura e padrões dos dados."
    ),
    (
        "🤖",
        "Copiloto de Negócios IA",
        "Transforme perguntas de negócio em insights acionáveis."
    ),
    (
        "⚙️",
        "Motor de AutoML",
        "Compare modelos de machine learning automaticamente."
    ),
    (
        "🎯",
        "Motor de Predição",
        "Gere predições com modelos treinados."
    ),
    

    (
        "📈",
        "Previsão de Negócios",
        "Identifique tendências futuras a partir do histórico."
    ),
    (
        "🚨",
        "Detecção de Anomalias",
        "Identifique registros incomuns e potencialmente arriscados."
    ),
    (
        "📄",
        "Relatórios Executivos",
        "Converta análises em relatórios prontos para a gestão."
    ),
]

for row_start in range(0, len(features), 2):

    left, right = st.columns(2)

    for column, feature in zip(
        [left, right],
        features[row_start:row_start + 2]
    ):

        icon, title, description = feature

        with column:

            st.markdown(
                textwrap.dedent(
                    f"""
                    <div class="feature-card">
                        <div class="feature-icon">{icon}</div>
                        <div class="feature-title">{title}</div>
                        <div class="feature-description">{description}</div>
                    </div>
                    """
                ),
                unsafe_allow_html=True
            )

st.markdown("---")


# =====================================================
# BUSINESS DOMAINS
# =====================================================

st.markdown(
    '<div class="section-title">🏢 Setores de Negócio Suportados</div>',
    unsafe_allow_html=True
)

domains = [
    "🛒 E-Commerce",
    "🏥 Saúde",
    "🏦 Bancos",
    "💰 Finanças",
    "🏭 Indústria",
    "🚚 Cadeia de Suprimentos",
    "📡 Telecomunicações",
    "🎓 Educação",
    "👨‍💼 Recursos Humanos",
    "📈 Vendas e Marketing",
]

domain_columns = st.columns(5)

for i, domain in enumerate(domains):

    with domain_columns[i % 5]:

        st.markdown(
            textwrap.dedent(
                f"""
                <div class="domain-card">{domain}</div>
                """
            ),
            unsafe_allow_html=True
        )

st.markdown("---")


# =====================================================
# DECISION WORKFLOW
# =====================================================

st.markdown(
    '<div class="section-title">🧭 Fluxo de Inteligência de Decisão</div>',
    unsafe_allow_html=True
)

workflow = [
    ("01", "📂", "Enviar"),
    ("02", "🔍", "Entender"),
    ("03", "⚙️", "Treinar"),
    ("04", "🎯", "Prever"),
    ("05", "🧠", "Explicar"),
    ("06", "📈", "Projetar"),
    ("07", "📊", "Decidir"),
    ("08", "📄", "Reportar"),
]

workflow_columns = st.columns(8)

for column, item in zip(
    workflow_columns,
    workflow
):

    number, icon, title = item

    with column:

        st.markdown(
            textwrap.dedent(
                f"""
                <div class="workflow-card">
                    <div class="workflow-number">{number}</div>
                    <div class="workflow-icon">{icon}</div>
                    <div class="workflow-title">{title}</div>
                </div>
                """
            ),
            unsafe_allow_html=True
        )

st.markdown("---")



# =====================================================
# AI INSIGHT
# =====================================================

st.markdown(
    '<div class="section-title">🤖 Insight da IA</div>',
    unsafe_allow_html=True
)

if len(uploads) == 0:

    insight = (
        "Seu ambiente está pronto. Envie um dataset de "
        "negócio para iniciar o fluxo de inteligência de "
        "decisão."
    )

elif len(models) == 0:

    insight = (
        "Há um dataset disponível. O próximo passo é analisar "
        "os dados e treinar um modelo de machine learning."
    )

elif len(predictions) == 0:

    insight = (
        "Seu ambiente tem modelos treinados. Agora "
        "você pode gerar predições ou explorar o "
        "desempenho e as análises dos modelos."
    )

else:

    insight = (
        "Seu ambiente de inteligência de decisão está ativo. "
        "Explore predições, previsões, detecção de anomalias "
        "e analytics executivo."
    )

st.markdown(
    textwrap.dedent(
        f"""
        <div class="ai-insight">
            🤖 <strong>Insight da Plataforma</strong><br><br>
            {insight}
        </div>
        """
    ),
    unsafe_allow_html=True
)

st.markdown("---")


# =====================================================
# NAVIGATION
# =====================================================

st.markdown(
    '<div class="section-title">🧭 Continuar</div>',
    unsafe_allow_html=True
)

n1, n2 = st.columns(2)

with n1:

    if st.button(
        "← Anterior",
        disabled=True,
        width="stretch"
    ):
        pass

with n2:

    if st.button(
        "Próximo → Enviar Dataset",
        width="stretch"
    ):
        st.switch_page("pages/1_Upload_Dataset.py")


# =====================================================
# FOOTER
# =====================================================

st.markdown(
    textwrap.dedent("""
    <div class="footer">
        © 2026 S Jashwanth · Nex Decision AI · Versão 2.2
    </div>
    """),
    unsafe_allow_html=True
)
