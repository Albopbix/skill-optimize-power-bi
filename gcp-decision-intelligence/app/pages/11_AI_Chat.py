
import streamlit as st
import pandas as pd
import numpy as np

from src.ai_chat.chat_engine import ChatEngine
from src.llm import gemini_client
from src.ui.layout import page_header, ai_insight, page_footer


# ==========================================================
# PAGE CONFIGURATION
# ==========================================================

st.set_page_config(
    page_title="Chatbot de Negócios IA",
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

    div.stButton > button {
        border-radius: 10px;
        min-height: 42px;
        font-weight: 600;
        transition: 0.2s ease;
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

    div[data-testid="stChatMessage"] {
        border-radius: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ==========================================================
# INITIALIZE SESSION STATE
# ==========================================================

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

if "chatbot_page" not in st.session_state:
    st.session_state["chatbot_page"] = "Overview"

if "chat_question" not in st.session_state:
    st.session_state["chat_question"] = ""

if "chat_dataset_signature" not in st.session_state:
    st.session_state["chat_dataset_signature"] = None


# ==========================================================
# PAGE HEADER
# ==========================================================

page_header(
    "🤖 Chatbot de Negócios IA",
    "Explore seus dados, faça perguntas em linguagem natural "
    "e descubra insights úteis para o negócio."
)


# ==========================================================
# CHECK DATASET
# ==========================================================

if "dataset" not in st.session_state:
    st.warning("⚠️ Envie um dataset primeiro.")
    st.info("Vá em Enviar Dataset, envie um arquivo CSV ou "
            "Excel e volte ao Chatbot de Negócios IA.")
    page_footer()
    st.stop()

df = st.session_state["dataset"]

if not isinstance(df, pd.DataFrame):
    st.error("O dataset carregado não é um DataFrame pandas válido.")
    page_footer()
    st.stop()

if df.empty:
    st.warning("Seu dataset não tem linhas.")
    page_footer()
    st.stop()


# ==========================================================
# RESET CHAT WHEN DATASET CHANGES
# ==========================================================

dataset_signature = (
    len(df),
    len(df.columns),
    tuple(str(column) for column in df.columns),
)

if (
    st.session_state["chat_dataset_signature"]
    != dataset_signature
):
    st.session_state["chat_history"] = []
    st.session_state["chat_dataset_signature"] = dataset_signature


# ==========================================================
# DATA PREPARATION
# ==========================================================

numeric_cols = df.select_dtypes(include=np.number).columns.tolist()

categorical_cols = df.select_dtypes(
    include=["object", "category", "bool", "string"]
).columns.tolist()

datetime_cols = df.select_dtypes(
    include=["datetime", "datetimetz"]
).columns.tolist()

missing_cells = int(df.isna().sum().sum())
duplicate_rows = int(df.duplicated().sum())
memory_mb = float(
    df.memory_usage(index=True, deep=True).sum() / (1024 ** 2)
)

engine = ChatEngine()

if gemini_client.is_enabled():
    st.caption(f"🧠 Com tecnologia Gemini (`{gemini_client.model_name()}`) no Vertex AI")


# ==========================================================
# REUSABLE CHAT FUNCTION
# ==========================================================

def ask_chatbot(question):
    """Ask the existing ChatEngine and store the conversation."""

    question = question.strip()

    if not question:
        st.warning("Digite uma pergunta.")
        return

    st.session_state["chat_history"].append(
        ("You", question)
    )

    try:
        with st.spinner("🤖 Analisando seu dataset..."):
            answer = engine.ask(
                df,
                question,
                history=st.session_state["chat_history"][:-1],
            )

        if answer is None:
            answer = "O motor de IA retornou uma resposta vazia."

        st.session_state["chat_history"].append(
            ("AI", str(answer))
        )

    except Exception as error:
        st.session_state["chat_history"].append(
            (
                "AI",
                "Não consegui processar essa pergunta. Tente reformulá-la "
                "ou verifique a configuração da IA. Detalhes técnicos: "
                f"{error}",
            )
        )


# ==========================================================
# NAVIGATION DEFINITIONS
# ==========================================================

nav_items = [
    ("Overview", "🏠 Visão Geral"),
    ("Chat", "💬 Chat"),
    ("Data Insights", "📊 Insights dos Dados"),
    ("Data Preview", "🗂️ Prévia dos Dados"),
    ("Help", "❓ Ajuda"),
]


# ==========================================================
# MAIN PAGE CONTENT
# ==========================================================

current_page = st.session_state["chatbot_page"]


# ----------------------------------------------------------
# PAGE 1: OVERVIEW
# ----------------------------------------------------------

if current_page == "Overview":

    st.subheader("📊 Visão Geral do Dataset")

    st.success("✅ Dataset carregado com sucesso")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("Total de Linhas", f"{len(df):,}")

    with c2:
        st.metric("Total de Colunas", f"{len(df.columns):,}")

    with c3:
        st.metric("Células Ausentes", f"{missing_cells:,}")

    with c4:
        st.metric("Linhas Duplicadas", f"{duplicate_rows:,}")

    c5, c6, c7 = st.columns(3)

    with c5:
        st.metric("Colunas Numéricas", len(numeric_cols))

    with c6:
        st.metric("Colunas Categóricas", len(categorical_cols))

    with c7:
        st.metric("Memória do Dataset", f"{memory_mb:.2f} MB")

    st.divider()

    st.subheader("🧠 O que seu assistente de IA pode fazer?")

    feature_cols = st.columns(3)

    with feature_cols[0]:
        st.markdown("### 🔍 Entender")
        st.write(
            "Pergunte sobre a estrutura do dataset, o "
            "significado das colunas, os tipos de dados "
            "e os resumos estatísticos."
        )

    with feature_cols[1]:
        st.markdown("### 📈 Analisar")
        st.write(
            "Explore valores ausentes, distribuições, correlações "
            "e possíveis problemas de qualidade dos dados."
        )

    with feature_cols[2]:
        st.markdown("### 💡 Descobrir")
        st.write(
            "Investigue padrões e faça perguntas que apoiem "
            "fluxos de negócio e de machine learning."
        )

    st.divider()

    st.subheader("🚀 Comece com uma pergunta")

    starter_questions = [
        "Quantas linhas e colunas tem meu dataset?",
        "Quais colunas têm mais valores ausentes?",
        "Resuma as colunas numéricas.",
        "Que pré-processamento devo considerar?",
    ]

    for i, prompt in enumerate(starter_questions):
        if st.button(
            f"💬 {prompt}",
            key=f"overview_prompt_{i}",
            use_container_width=True,
        ):
            st.session_state["chatbot_page"] = "Chat"
            st.session_state["chat_history"].append(
                ("You", prompt)
            )

            try:
                with st.spinner("🤖 Analisando seu dataset..."):
                    answer = engine.ask(
                        df,
                        prompt,
                        history=st.session_state["chat_history"][:-1],
                    )

                st.session_state["chat_history"].append(
                    (
                        "AI",
                        str(answer) if answer is not None
                        else "O motor de IA retornou uma resposta vazia.",
                    )
                )

            except Exception as error:
                st.session_state["chat_history"].append(
                    (
                        "AI",
                        f"Não foi possível processar a pergunta: {error}",
                    )
                )

            st.rerun()


# ----------------------------------------------------------
# PAGE 2: CHAT
# ----------------------------------------------------------

elif current_page == "Chat":

    st.subheader("💬 Converse com seus Dados")

    st.caption(
        "Faça perguntas sobre o dataset carregado em linguagem natural."
    )

    with st.expander("💡 Perguntas sugeridas", expanded=True):

        prompt_options = [
            "Quantas linhas tem meu dataset?",
            "Qual coluna tem mais valores ausentes?",
            "Quais são as colunas numéricas?",
            "Resuma meu dataset.",
            "Que pré-processamento devo fazer?",
            "Este dataset é adequado para predição?",
            "Quais colunas têm valores incomuns?",
            "Explique as relações entre as colunas numéricas.",
        ]

        selected_prompt = st.selectbox(
            "Escolha uma pergunta",
            prompt_options,
            key="suggested_chat_prompt",
        )

        if st.button(
            "Usar pergunta sugerida",
            key="use_suggested_prompt",
        ):
            st.session_state["chat_question"] = selected_prompt
            st.rerun()

    with st.form("chat_question_form", clear_on_submit=True):

        question = st.text_input(
            "Faça uma pergunta sobre seu dataset",
            placeholder="Exemplo: Quais colunas têm valores ausentes?",
            key="chat_form_question",
        )

        ask = st.form_submit_button(
            "🤖 Perguntar à IA",
            use_container_width=True,
        )

    if ask:
        if question.strip():
            ask_chatbot(question)
        else:
            st.warning("Digite uma pergunta.")

    c1, c2 = st.columns(2)

    with c1:
        if st.button(
            "🗑️ Limpar conversa",
            use_container_width=True,
        ):
            st.session_state["chat_history"] = []
            st.rerun()

    with c2:
        conversation_text = "\n\n".join(
            f"{sender}: {message}"
            for sender, message in st.session_state["chat_history"]
        )

        st.download_button(
            "📥 Exportar conversa",
            data=conversation_text or "Nenhuma conversa ainda.",
            file_name="ai_chat_conversation.txt",
            mime="text/plain",
            use_container_width=True,
        )

    st.divider()

    st.subheader("📝 Histórico da Conversa")

    if not st.session_state["chat_history"]:
        st.info(
            "Sua conversa aparecerá aqui. Comece "
            "fazendo uma pergunta acima."
        )

    else:
        for sender, message in st.session_state["chat_history"]:

            if sender == "You":
                with st.chat_message("user"):
                    st.write(message)

            else:
                with st.chat_message("assistant", avatar="🤖"):
                    st.markdown(message)


# ----------------------------------------------------------
# PAGE 3: DATA INSIGHTS
# ----------------------------------------------------------

elif current_page == "Data Insights":

    st.subheader("📊 Insights e Qualidade dos Dados")

    st.write(
        "Explore resumos estatísticos e problemas comuns de "
        "qualidade dos dados antes de construir um modelo "
        "de machine learning."
    )

    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "Valores Ausentes",
            "Estatísticas",
            "Correlações",
            "Perfis das Colunas",
        ]
    )

    # Missing values
    with tab1:

        missing_report = pd.DataFrame({
            "Coluna": df.columns.astype(str),
            "Qtd. Ausentes": df.isna().sum().values,
            "Percentual Ausente": (
                df.isna().mean().values * 100
            ).round(2),
            "Tipo de Dado": df.dtypes.astype(str).values,
        })

        missing_report = missing_report.sort_values(
            "Qtd. Ausentes",
            ascending=False,
        )

        st.dataframe(
            missing_report,
            use_container_width=True,
            hide_index=True,
        )

        if missing_cells == 0:
            st.success("Nenhum valor ausente foi detectado.")
        else:
            st.warning(
                f"Foram encontradas {missing_cells:,} células "
                "ausentes. Revise as colunas afetadas antes "
                "de modelar."
            )

    # Numeric statistics
    with tab2:

        if numeric_cols:
            st.dataframe(
                df[numeric_cols].describe().T.round(3),
                use_container_width=True,
            )
        else:
            st.info("Não há colunas numéricas disponíveis.")

    # Correlations
    with tab3:

        if len(numeric_cols) >= 2:

            correlation = df[numeric_cols].corr(
                numeric_only=True
            )

            st.dataframe(
                correlation.round(3),
                use_container_width=True,
            )

            try:
                import plotly.express as px

                fig = px.imshow(
                    correlation,
                    text_auto=".2f",
                    aspect="auto",
                    color_continuous_scale="RdBu_r",
                    zmin=-1,
                    zmax=1,
                    title="Matriz de Correlação das Variáveis Numéricas",
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True,
                )

            except Exception as error:
                st.caption(
                    "A tabela de correlação está disponível; "
                    "o mapa de calor não pôde ser exibido: "
                    f"{error}"
                )

        else:
            st.info(
                "São necessárias pelo menos duas colunas "
                "numéricas para calcular correlações."
            )

    # Column profiles
    with tab4:

        selected_column = st.selectbox(
            "Selecione uma coluna",
            df.columns.tolist(),
            format_func=str,
        )

        series = df[selected_column]

        p1, p2, p3 = st.columns(3)

        with p1:
            st.metric("Tipo de Dado", str(series.dtype))

        with p2:
            st.metric("Valores Únicos", int(series.nunique()))

        with p3:
            st.metric("Valores Ausentes", int(series.isna().sum()))

        st.markdown("**Valores mais frequentes**")

        value_counts = (
            series.astype("string")
            .fillna("(Ausente)")
            .value_counts()
            .head(10)
            .rename_axis("Valor")
            .reset_index(name="Contagem")
        )

        st.dataframe(
            value_counts,
            use_container_width=True,
            hide_index=True,
        )


# ----------------------------------------------------------
# PAGE 4: DATA PREVIEW
# ----------------------------------------------------------

elif current_page == "Data Preview":

    st.subheader("🗂️ Explorador de Dados")

    st.write(
        "Inspecione registros, escolha as colunas a "
        "exibir e baixe uma cópia do seu dataset."
    )

    st.caption(
        f"Dimensões do dataset: {len(df):,} "
        f"linhas × {len(df.columns):,} colunas"
    )

    selected_columns = st.multiselect(
        "Escolha as colunas a exibir",
        options=df.columns.tolist(),
        default=df.columns.tolist(),
        format_func=str,
    )

    if selected_columns:

        preview_rows = st.slider(
            "Número de linhas na prévia",
            min_value=5,
            max_value=max(5, min(len(df), 500)),
            value=min(len(df), 50),
            step=5,
        )

        st.dataframe(
            df[selected_columns].head(preview_rows),
            use_container_width=True,
            hide_index=True,
        )

        st.download_button(
            "📥 Baixar colunas selecionadas em CSV",
            data=df[selected_columns].to_csv(index=False).encode("utf-8"),
            file_name="dataset_selected_columns.csv",
            mime="text/csv",
            use_container_width=True,
        )

    else:
        st.info("Selecione pelo menos uma coluna para visualizar os dados.")

    st.divider()

    st.subheader("🔎 Estrutura do Dataset")

    structure = pd.DataFrame({
        "Coluna": df.columns.astype(str),
        "Tipo de Dado": df.dtypes.astype(str).values,
        "Valores Não Nulos": df.notna().sum().values,
        "Valores Ausentes": df.isna().sum().values,
        "Valores Únicos": df.nunique().values,
    })

    st.dataframe(
        structure,
        use_container_width=True,
        hide_index=True,
    )


# ----------------------------------------------------------
# PAGE 5: HELP
# ----------------------------------------------------------

elif current_page == "Help":

    st.subheader("❓ Ajuda e Guia de Uso")

    with st.expander("Como começo?", expanded=True):
        st.markdown(
            """
            1. Envie um dataset na página Enviar Dataset.
            2. Abra o Chatbot de Negócios IA.
            3. Selecione **Chat** nos botões de navegação.
            4. Digite uma pergunta sobre seu dataset.
            5. Revise a resposta e use Insights dos Dados para
               informações estatísticas adicionais.
            """
        )

    with st.expander("Que perguntas posso fazer?"):
        st.markdown(
            """
            - Quantas linhas e colunas existem?
            - Quais colunas têm valores ausentes?
            - Quais são as distribuições das colunas numéricas?
            - Que pré-processamento pode ser necessário?
            - Quais colunas numéricas estão correlacionadas?
            - O que devo investigar antes de treinar um modelo?
            """
        )

    with st.expander("As respostas são confiáveis?"):
        st.markdown(
            """
            As respostas da IA podem ser incompletas ou incorretas. Confira
            conclusões importantes no dataset real e nos resumos
            estatísticos. Correlação não estabelece causalidade, e a
            adequação para predição depende da variável-alvo, da
            qualidade dos dados e do objetivo da modelagem.
            """
        )

    with st.expander("Solução de problemas"):
        st.markdown(
            """
            - **Sem dataset:** envie um antes de abrir o chatbot.
            - **Erro da IA:** verifique a configuração do Gemini
              (GEMINI_ENABLED, projeto e permissões do Vertex AI).
            - **Resultado inesperado:** reformule a pergunta e compare
              a resposta com a página Insights dos Dados.
            - **Dataset grande:** use uma prévia menor para facilitar
              a inspeção.
            """
        )


# ==========================================================
# AI INSIGHT
# ==========================================================

st.divider()

ai_insight(
    "O Chatbot de Negócios IA combina perguntas em linguagem natural "
    "com exploração do dataset, resumos estatísticos, verificações "
    "de qualidade dos dados e histórico da conversa. Valide as "
    "conclusões geradas pela IA com os dados de origem."
)
# ==========================================================
# PREVIOUS / NEXT PAGE NAVIGATION
# ==========================================================

st.divider()
st.subheader("🧭 Navegação")

col_prev, col_home, col_next = st.columns(3)

with col_prev:
    if st.button("⬅️ Página anterior", use_container_width=True):
        st.switch_page("pages/9_Interactive_Dashboard.py")

with col_home:
    if st.button("🏠 Início", use_container_width=True):
        st.switch_page("pages/0_Home.py")

with col_next:
    if st.button("Próxima página ➡️", use_container_width=True):
        st.switch_page("pages/12_Dataset_History.py")



# ==========================================================
# FOOTER
# ==========================================================

page_footer()
