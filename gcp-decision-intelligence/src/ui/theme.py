import streamlit as st


def sidebar():

    st.sidebar.title("🤖 Inteligência de Decisão com IA")

    st.sidebar.markdown("---")

    # ==========================================
    # DATASET STATUS
    # ==========================================

    st.sidebar.subheader("📂 Status do Dataset")

    if "dataset" in st.session_state:

        df = st.session_state["dataset"]

        st.sidebar.success("Dataset carregado")

        st.sidebar.metric("Linhas", f"{len(df):,}")

        st.sidebar.metric("Colunas", len(df.columns))

        missing = int(df.isnull().sum().sum())

        duplicates = int(df.duplicated().sum())

        st.sidebar.metric("Ausentes", missing)

        st.sidebar.metric("Duplicados", duplicates)

        score = 100

        score -= min(missing * 2, 30)

        score -= min(duplicates * 2, 20)

        score = max(score, 0)

        st.sidebar.metric("Score de Saúde", f"{score}/100")

    else:

        st.sidebar.warning("Nenhum dataset carregado")

    st.sidebar.markdown("---")

    # ==========================================
    # SYSTEM STATUS
    # ==========================================

    st.sidebar.subheader("⚙️ Status do Sistema")

    st.sidebar.success("Motor de IA pronto")

    st.sidebar.success("AutoML disponível")

    st.sidebar.success("Previsão pronta")

    st.sidebar.success("Relatórios habilitados")

    st.sidebar.markdown("---")

    # ==========================================
    # QUICK HELP
    # ==========================================

    st.sidebar.subheader("💡 Início Rápido")

    st.sidebar.write("1️⃣ Enviar dataset")

    st.sidebar.write("2️⃣ Analisar dataset")

    st.sidebar.write("3️⃣ Treinar AutoML")

    st.sidebar.write("4️⃣ Prever")

    st.sidebar.write("5️⃣ Gerar relatório")

    st.sidebar.markdown("---")

    # ==========================================
    # FOOTER
    # ==========================================

    st.sidebar.caption("Inteligência de Decisão com IA")

    st.sidebar.caption("Suíte de Analytics Empresarial")

    st.sidebar.caption("Versão 2.0")