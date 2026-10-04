import streamlit as st
import pandas as pd
import textwrap

from src.ui.layout import (
    page_header,
    ai_insight,
    page_footer
)

from src.business_copilot.copilot_engine import BusinessCopilot
from src.llm import gemini_client


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Copiloto de Negócios IA | Nex Decision AI",
    page_icon="🤖",
    layout="wide"
)


# =========================================================
# CUSTOM UI
# =========================================================

st.markdown(
    textwrap.dedent(
        """
        <style>

        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 2rem;
        }

        .copilot-hero {
            padding: 30px;
            border-radius: 20px;
            background: linear-gradient(
                135deg,
                rgba(37,99,235,0.18),
                rgba(124,58,237,0.15)
            );
            border: 1px solid rgba(148,163,184,0.18);
            margin-bottom: 24px;
        }

        .copilot-title {
            font-size: 34px;
            font-weight: 850;
            margin-bottom: 8px;
        }

        .copilot-subtitle {
            font-size: 16px;
            color: #94a3b8;
            line-height: 1.6;
        }

        .dataset-badge {
            display: inline-block;
            margin-top: 14px;
            padding: 7px 14px;
            border-radius: 20px;
            background: rgba(59,130,246,0.12);
            border: 1px solid rgba(59,130,246,0.25);
            color: #bfdbfe;
            font-size: 13px;
        }

        .decision-card {
            padding: 22px;
            border-radius: 16px;
            background: rgba(15,23,42,0.45);
            border: 1px solid rgba(148,163,184,0.14);
            min-height: 145px;
        }

        .decision-icon {
            font-size: 28px;
            margin-bottom: 8px;
        }

        .decision-title {
            font-size: 15px;
            font-weight: 750;
            margin-bottom: 7px;
        }

        .decision-text {
            font-size: 13px;
            color: #94a3b8;
            line-height: 1.55;
        }

        .score-card {
            padding: 25px;
            border-radius: 18px;
            background: rgba(15,23,42,0.48);
            border: 1px solid rgba(148,163,184,0.15);
            text-align: center;
        }

        .score-value {
            font-size: 48px;
            font-weight: 850;
        }

        .score-label {
            color: #94a3b8;
            font-size: 13px;
        }

        .recommendation-card {
            padding: 17px 20px;
            border-radius: 13px;
            background: rgba(30,41,59,0.48);
            border-left: 4px solid #6366f1;
            margin-bottom: 10px;
        }

        .risk-card {
            padding: 17px 20px;
            border-radius: 13px;
            background: rgba(127,29,29,0.14);
            border-left: 4px solid #ef4444;
            margin-bottom: 10px;
        }

        .opportunity-card {
            padding: 17px 20px;
            border-radius: 13px;
            background: rgba(20,83,45,0.14);
            border-left: 4px solid #22c55e;
            margin-bottom: 10px;
        }

        .action-card {
            padding: 22px;
            border-radius: 16px;
            background: linear-gradient(
                135deg,
                rgba(37,99,235,0.14),
                rgba(99,102,241,0.10)
            );
            border: 1px solid rgba(99,102,241,0.25);
        }

        .action-title {
            font-size: 14px;
            color: #94a3b8;
            margin-bottom: 8px;
        }

        .action-text {
            font-size: 19px;
            font-weight: 750;
            line-height: 1.4;
        }

        .question-card {
            padding: 13px 16px;
            border-radius: 11px;
            background: rgba(30,41,59,0.40);
            border: 1px solid rgba(148,163,184,0.12);
            margin-bottom: 8px;
        }

        .section-title {
            font-size: 21px;
            font-weight: 780;
            margin-top: 20px;
            margin-bottom: 14px;
        }

        </style>
        """
    ),
    unsafe_allow_html=True
)


# =========================================================
# HEADER
# =========================================================

page_header(
    "🤖 Copiloto de Negócios IA",
    "Transforme seu dataset em perguntas de negócio, insights, riscos e decisões acionáveis."
)


# =========================================================
# CHECK DATASET
# =========================================================

if "dataset" not in st.session_state:

    st.warning(
        "📂 Envie um dataset primeiro."
    )

    st.info(
        "Vá em **Enviar Dataset** e envie o dataset do seu negócio."
    )

    if st.button(
        "📂 Ir para Enviar Dataset"
    ):
        st.switch_page(
            "pages/1_Upload_Dataset.py"
        )

    st.stop()


# =========================================================
# LOAD DATASET
# =========================================================

df = st.session_state["dataset"]

filename = st.session_state.get(
    "filename",
    "Dataset enviado"
)


if df is None or df.empty:

    st.error(
        "❌ O dataset atual está vazio ou indisponível."
    )

    st.stop()


# =========================================================
# COPILOT HERO
# =========================================================

st.markdown(
    textwrap.dedent(
        f"""
        <div class="copilot-hero">
            <div class="copilot-title">
                🧠 Central de Inteligência de Decisão
            </div>
            <div class="copilot-subtitle">
                O Nex Decision AI conecta seu dataset ao
                raciocínio de negócio para identificar riscos,
                oportunidades e decisões acionáveis.
            </div>
            <div class="dataset-badge">
                📄 Dataset ativo: {filename}
            </div>
        </div>
        """
    ),
    unsafe_allow_html=True
)


# =========================================================
# INITIALIZE COPILOT
# =========================================================

try:

    copilot = BusinessCopilot(df)

    summary = copilot.executive_summary()

    raw_score = copilot.business_score()

except Exception as e:

    st.error(
        "⚠️ O Copiloto de Negócios IA não conseguiu analisar este dataset."
    )

    with st.expander(
        "Detalhes técnicos"
    ):

        st.write(str(e))

    st.stop()


# =========================================================
# BUSINESS SCORE
# =========================================================

try:

    score = float(raw_score)

except Exception:

    score = 0


score = max(
    0,
    min(
        100,
        score
    )
)


if score >= 90:

    score_status = "Excelente"
    score_message = (
        "O dataset está em ótimas condições para os fluxos de decisão."
    )

elif score >= 75:

    score_status = "Bom"
    score_message = (
        "O dataset é, em geral, adequado para análises de negócio."
    )

elif score >= 60:

    score_status = "Moderado"
    score_message = (
        "Algumas melhorias podem ser necessárias antes de modelagens avançadas."
    )

else:

    score_status = "Requer atenção"
    score_message = (
        "Problemas importantes nos dados devem ser resolvidos antes de decisões relevantes."
    )


# =========================================================
# DECISION SNAPSHOT
# =========================================================

st.markdown(
    '<div class="section-title">🎯 Retrato Executivo da Decisão</div>',
    unsafe_allow_html=True
)

c1, c2, c3 = st.columns(3)

with c1:

    st.markdown(
        textwrap.dedent(
            f"""
            <div class="score-card">
                <div class="score-value">
                    {score:.0f}
                </div>
                <div class="score-label">
                    SCORE DE SAÚDE DO NEGÓCIO
                </div>
                <br>
                <strong>{score_status}</strong>
            </div>
            """
        ),
        unsafe_allow_html=True
    )

with c2:

    st.markdown(
        textwrap.dedent(
            f"""
            <div class="decision-card">
                <div class="decision-icon">🧠</div>
                <div class="decision-title">
                    Avaliação da IA
                </div>
                <div class="decision-text">
                    {score_message}
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
            <div class="decision-card">
                <div class="decision-icon">📌</div>
                <div class="decision-title">
                    Contexto de Decisão Ativo
                </div>
                <div class="decision-text">
                    O Nex Decision AI está usando
                    <strong>{filename}</strong>
                    como contexto de negócio atual.
                </div>
            </div>
            """
        ),
        unsafe_allow_html=True
    )


st.progress(
    score / 100
)


# =========================================================
# AI RECOMMENDATIONS
# =========================================================

st.markdown(
    '<div class="section-title">🤖 Ações Recomendadas pela IA</div>',
    unsafe_allow_html=True
)

try:

    recommendations = copilot.recommendations()

except Exception:

    recommendations = []


if recommendations:

    for recommendation in recommendations:

        st.markdown(
            textwrap.dedent(
                f"""
                <div class="recommendation-card">
                    💡 <strong>Recomendação</strong><br>
                    {recommendation}
                </div>
                """
            ),
            unsafe_allow_html=True
        )

else:

    st.info(
        "Nenhuma recomendação adicional foi gerada."
    )


# =========================================================
# PRIORITY ACTION
# =========================================================

st.markdown(
    '<div class="section-title">⚡ Próxima Ação Recomendada</div>',
    unsafe_allow_html=True
)


if score < 60:

    next_action = (
        "Melhore a qualidade dos dados antes de construir modelos preditivos."
    )

elif score < 75:

    next_action = (
        "Investigue os valores ausentes e os registros duplicados."
    )

elif score < 90:

    next_action = (
        "Siga para o AutoML ou para as previsões para descobrir padrões preditivos."
    )

else:

    next_action = (
        "Avance para a modelagem preditiva e a análise de decisões de negócio."
    )


st.markdown(
    textwrap.dedent(
        f"""
        <div class="action-card">
            <div class="action-title">
                RECOMENDAÇÃO DO NEX DECISION AI
            </div>
            <div class="action-text">
                ⚡ {next_action}
            </div>
        </div>
        """
    ),
    unsafe_allow_html=True
)


# =========================================================
# BUSINESS RISKS
# =========================================================

st.markdown(
    '<div class="section-title">🚨 Sinais de Risco para o Negócio</div>',
    unsafe_allow_html=True
)

risks = []


if summary.get("Missing", 0) > 0:

    risks.append(
        "Valores ausentes podem reduzir a confiabilidade das análises seguintes."
    )


if summary.get("Duplicates", 0) > 0:

    risks.append(
        "Registros duplicados podem distorcer padrões e o treino de modelos."
    )


if len(df) < 100:

    risks.append(
        "O dataset tem relativamente poucos registros para uma modelagem preditiva confiável."
    )


if len(df.columns) < 5:

    risks.append(
        "O dataset tem um número limitado de variáveis disponíveis."
    )


if risks:

    for risk in risks:

        st.markdown(
            textwrap.dedent(
                f"""
                <div class="risk-card">
                    🚨 {risk}
                </div>
                """
            ),
            unsafe_allow_html=True
        )

else:

    st.success(
        "🟢 Nenhum sinal relevante de risco para o negócio detectado."
    )


# =========================================================
# BUSINESS OPPORTUNITIES
# =========================================================

st.markdown(
    '<div class="section-title">🚀 Áreas de Oportunidade com IA</div>',
    unsafe_allow_html=True
)


opportunities = [
    (
        "📈 Analytics Preditivo",
        "Use padrões históricos para estimar resultados futuros."
    ),
    (
        "👥 Inteligência de Clientes",
        "Identifique comportamentos de clientes e oportunidades de segmentação."
    ),
    (
        "⏳ Previsões",
        "Detecte tendências e estime a evolução futura do negócio."
    ),
    (
        "🚨 Detecção de Anomalias",
        "Identifique registros incomuns e exceções potencialmente importantes."
    ),
    (
        "📊 Inteligência Executiva",
        "Converta resultados analíticos em painéis prontos para decisão."
    ),
    (
        "⚙️ Automação",
        "Reduza trabalho repetitivo de análise e relatórios."
    )
]


opportunity_cols = st.columns(3)

for index, (title, description) in enumerate(
    opportunities
):

    with opportunity_cols[
        index % 3
    ]:

        st.markdown(
            textwrap.dedent(
                f"""
                <div class="opportunity-card">
                    <strong>{title}</strong>
                    <br><br>
                    <span style="color:#94a3b8;">
                        {description}
                    </span>
                </div>
                """
            ),
            unsafe_allow_html=True
        )


# =========================================================
# BUSINESS QUESTION CENTER
# =========================================================

st.markdown(
    '<div class="section-title">🎯 Central de Perguntas de Negócio</div>',
    unsafe_allow_html=True
)

st.caption(
    "Faça perguntas em linguagem de negócio. O Copiloto "
    "usará o dataset ativo como contexto."
)


question_categories = {

    "📊 Entender o Negócio": [
        "Resuma as descobertas mais importantes",
        "Quais são os padrões mais importantes?",
        "O que um executivo precisa saber sobre este dataset?"
    ],

    "🚨 Encontrar Problemas": [
        "Quais são os maiores riscos?",
        "Quais problemas existem neste dataset?",
        "Quais áreas precisam de atenção imediata?"
    ],

    "🚀 Encontrar Oportunidades": [
        "Onde estão as maiores oportunidades?",
        "Quais melhorias de negócio você recomenda?",
        "Como este dataset pode gerar valor para o negócio?"
    ],

    "🤖 Machine Learning": [
        "Quão pronto este dataset está para machine learning?",
        "Quais problemas de predição podem ser resolvidos?",
        "Qual abordagem de machine learning deve ser considerada?"
    ]

}


category = st.selectbox(
    "Escolha uma área de decisão",
    list(question_categories.keys())
)


selected_question = st.selectbox(
    "Escolha uma pergunta de negócio",
    [""] + question_categories[category]
)


custom_question = st.text_input(
    "Ou faça sua própria pergunta",
    placeholder="Exemplo: Quais áreas do negócio precisam de atenção?"
)


question = (
    custom_question.strip()
    if custom_question.strip()
    else selected_question
)


# =========================================================
# AI CHAT
# =========================================================

if question:

    with st.spinner(
        "🤖 O Nex Decision AI está analisando seu dataset..."
    ):

        try:

            answer = copilot.ask(
                question
            )

            st.markdown(
                '<div class="section-title">🧠 Decisão do Copiloto</div>',
                unsafe_allow_html=True
            )

            if hasattr(
                answer,
                "shape"
            ):

                st.dataframe(
                    answer,
                    width="stretch",
                    hide_index=True
                )

            elif isinstance(
                answer,
                list
            ):

                for item in answer:

                    st.markdown(
                        textwrap.dedent(
                            f"""
                            <div class="recommendation-card">
                                💡 {item}
                            </div>
                            """
                        ),
                        unsafe_allow_html=True
                    )

            elif isinstance(
                answer,
                tuple
            ):

                st.write(answer)

            else:

                st.info(
                    str(answer)
                )

            if copilot.last_engine == "gemini":
                st.caption(
                    f"🧠 Gemini (`{gemini_client.model_name()}`) no Vertex "
                    "AI — baseado no perfil do dataset; valide os números-chave."
                )

            elif copilot.last_error:
                st.caption(
                    "⚠️ Gemini indisponível; exibindo resposta do motor de regras."
                )

        except Exception as e:

            st.warning(
                "O Nex Decision AI não conseguiu gerar uma "
                "resposta para esta pergunta com o dataset "
                "atual."
            )

            with st.expander(
                "Detalhes técnicos"
            ):

                st.write(str(e))


# =========================================================
# AI INSIGHT
# =========================================================

ai_insight(
    "O Copiloto de Negócios converte a inteligência do "
    "dataset em perguntas, riscos, oportunidades e ações "
    "recomendadas orientadas ao negócio. Use-o como camada "
    "de decisão antes de seguir para a modelagem preditiva."
)


# =========================================================
# NAVIGATION
# =========================================================

st.divider()

previous_col, center_col, next_col = st.columns(
    [1, 2, 1]
)

with previous_col:

    if st.button(
        "⬅️ Anterior",
        width="stretch"
    ):

        st.switch_page(
            "pages/2_Dataset_Intelligence.py"
        )

with center_col:

    st.markdown(
        '<div style="text-align:center;color:#64748b;font-size:12px;">Etapa 3 do fluxo de inteligência</div>',
        unsafe_allow_html=True
    )

with next_col:

    if st.button(
        "Próximo ➡️",
        width="stretch"
    ):

        st.switch_page(
            "pages/4_Executive_Dashboard.py"
        )


# =========================================================
# FOOTER
# =========================================================

page_footer()