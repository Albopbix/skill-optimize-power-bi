import os
import hashlib
from datetime import datetime
from io import BytesIO

import pandas as pd
import streamlit as st
import plotly.express as px

from src.ui.layout import page_header, ai_insight, page_footer
from src.model_prediction.predictor import Predictor
from src.model_prediction.prediction_export import PredictionExporter
from src.database.database import Database
from src.storage import model_store


# =========================================================
# PAGE CONFIGURATION
# =========================================================
st.set_page_config(
    page_title="Estúdio de Predição | Nex Decision AI",
    page_icon="🔮",
    layout="wide",
)

RESULTS_KEY = "page7_prediction_results"
META_KEY = "page7_prediction_metadata"


# =========================================================
# HELPERS
# =========================================================
def file_fingerprint(uploaded_file):
    """Create a content-based signature so changed files invalidate old results."""
    content = uploaded_file.getvalue()
    return hashlib.sha256(content).hexdigest()


def safe_csv_bytes(dataframe):
    return dataframe.to_csv(index=False).encode("utf-8-sig")


def prediction_is_numeric(series):
    converted = pd.to_numeric(series, errors="coerce")
    return pd.api.types.is_numeric_dtype(series) or converted.notna().all()


def format_number(value):
    try:
        return f"{float(value):,.4g}"
    except (TypeError, ValueError):
        return str(value)


def section_heading(title, subtitle=None):
    st.subheader(title)
    if subtitle:
        st.caption(subtitle)


# =========================================================
# HEADER
# =========================================================
page_header(
    "🔮 Estúdio de Predição",
    "Execute modelos de machine learning salvos, verifique a qualidade "
    "da entrada, entenda o comportamento das predições e exporte resultados "
    "reproduzíveis.",
)

# =========================================================
# MODEL DISCOVERY
# =========================================================
try:
    models = model_store.list_models()
except Exception as exc:
    st.error(
        "Não foi possível listar os modelos salvos. Verifique "
        "a configuração de armazenamento de modelos (GCS_BUCKET "
        "/ permissões)."
    )
    with st.expander("Detalhes técnicos"):
        st.code(str(exc))
    page_footer()
    st.stop()

if not models:
    st.warning("Nenhum modelo .pkl salvo foi encontrado.")
    st.info("Abra o AutoML, treine um modelo e salve/exporte-o primeiro.")
    page_footer()
    st.stop()

# =========================================================
# CONFIGURATION
# =========================================================
section_heading("1. Configurar uma execução de predição")

config_left, config_right = st.columns([1, 1])

with config_left:
    selected_model = st.selectbox(
        "Modelo salvo",
        options=models,
        key="page7_selected_model",
    )

with config_right:
    uploaded_file = st.file_uploader(
        "Dataset de entrada (CSV)",
        type=["csv"],
        help="O CSV deve conter as colunas de variáveis usadas no treino.",
        key="page7_uploaded_csv",
    )

if uploaded_file is None:
    st.info("Escolha um modelo salvo e envie um CSV para começar.")
    ai_insight(
        "Para predições confiáveis, use as mesmas definições de variáveis "
        "e unidades usadas no treino do modelo."
    )
    page_footer()
    st.stop()

# =========================================================
# LOAD CSV
# =========================================================
try:
    raw_bytes = uploaded_file.getvalue()
    df = pd.read_csv(BytesIO(raw_bytes))
except Exception as exc:
    st.error(f"Não foi possível ler este arquivo CSV: {exc}")
    page_footer()
    st.stop()

if df.empty:
    st.warning("O CSV enviado não tem linhas de dados.")
    page_footer()
    st.stop()

if len(df.columns) == 0:
    st.warning("O CSV enviado não tem colunas.")
    page_footer()
    st.stop()

if df.columns.duplicated().any():
    duplicates = df.columns[df.columns.duplicated()].astype(str).tolist()
    st.error("Foram encontrados nomes de colunas duplicados: " + ", ".join(duplicates))
    st.info("Renomeie as colunas duplicadas no CSV e envie novamente.")
    page_footer()
    st.stop()

# Include content hash: same filename and size can still contain different data.
input_signature = (
    selected_model,
    uploaded_file.name,
    len(raw_bytes),
    file_fingerprint(uploaded_file),
)

previous_metadata = st.session_state.get(META_KEY)
if previous_metadata and previous_metadata.get("input_signature") != input_signature:
    st.session_state.pop(RESULTS_KEY, None)
    st.session_state.pop(META_KEY, None)

# =========================================================
# INPUT HEALTH
# =========================================================
section_heading("2. Saúde dos dados de entrada")

row_count, column_count = df.shape
missing_cells = int(df.isna().sum().sum())
duplicate_rows = int(df.duplicated().sum())
columns_with_missing = int(df.isna().any(axis=0).sum())
constant_columns = [
    str(col) for col in df.columns if df[col].nunique(dropna=False) <= 1
]
memory_mb = df.memory_usage(deep=True).sum() / (1024 * 1024)

h1, h2, h3, h4, h5 = st.columns(5)
h1.metric("Linhas", f"{row_count:,}")
h2.metric("Colunas", f"{column_count:,}")
h3.metric("Células ausentes", f"{missing_cells:,}")
h4.metric("Linhas duplicadas", f"{duplicate_rows:,}")
h5.metric("Memória aprox.", f"{memory_mb:.2f} MB")

with st.expander("Abrir relatório detalhado de qualidade dos dados"):
    missing_tab, types_tab, risk_tab = st.tabs(
        ["Valores ausentes", "Perfil das colunas", "Riscos potenciais"]
    )

    with missing_tab:
        missing_report = pd.DataFrame({
            "Coluna": df.columns.astype(str),
            "Qtd. ausentes": df.isna().sum().values,
            "% ausentes": (df.isna().mean().values * 100).round(2),
        })
        missing_report = missing_report[missing_report["Qtd. ausentes"] > 0]
        if missing_report.empty:
            st.success("Nenhum valor ausente detectado.")
        else:
            st.dataframe(missing_report, width="stretch", hide_index=True)

    with types_tab:
        profile = pd.DataFrame({
            "Coluna": df.columns.astype(str),
            "Tipo de dado": df.dtypes.astype(str).values,
            "Valores distintos": [df[col].nunique(dropna=True) for col in df.columns],
            "Qtd. ausentes": df.isna().sum().values,
        })
        st.dataframe(profile, width="stretch", hide_index=True)

    with risk_tab:
        if duplicate_rows:
            st.warning(f"Há {duplicate_rows:,} linhas duplicadas.")
        else:
            st.success("Nenhuma linha duplicada detectada.")
        if constant_columns:
            st.warning("Colunas constantes: " + ", ".join(constant_columns))
        else:
            st.success("Nenhuma coluna constante detectada.")
        if missing_cells:
            st.warning(
                "Valores ausentes não são preenchidos nem removidos automaticamente. "
                "O pipeline de pré-processamento do modelo precisa saber tratá-los."
            )

# =========================================================
# DATA PREVIEW
# =========================================================
with st.expander("Prévia do dataset enviado", expanded=True):
    preview_count = st.slider(
        "Linhas na prévia",
        min_value=1,
        max_value=min(100, row_count),
        value=min(10, row_count),
        key="page7_preview_rows",
    )
    st.dataframe(df.head(preview_count), width="stretch", hide_index=True)

# =========================================================
# LOAD MODEL AND VALIDATE FEATURES
# =========================================================
section_heading("3. Compatibilidade do modelo")

try:
    model_path = model_store.get_model_path(selected_model)
    predictor = Predictor(model_path)
except Exception as exc:
    st.error(
        "Não foi possível carregar o modelo selecionado. O arquivo pode "
        "estar corrompido ou ser incompatível com o projeto atual."
    )
    with st.expander("Detalhes técnicos"):
        st.code(str(exc))
    page_footer()
    st.stop()

missing_features, extra_features = predictor.validate_features(df)
feature_left, feature_right = st.columns(2)

with feature_left:
    if missing_features:
        st.error(f"Variáveis obrigatórias ausentes ({len(missing_features)})")
        st.write(missing_features)
    else:
        st.success("Todas as variáveis exigidas pelo modelo estão presentes.")

with feature_right:
    if extra_features:
        st.info(f"{len(extra_features)} coluna(s) extra(s) será(ão) ignorada(s).")
        st.write(extra_features)
    else:
        st.success("Nenhuma coluna extra para ignorar.")

with st.expander("Variáveis exigidas pelo modelo"):
    st.write(list(predictor.feature_names))
    st.caption(
        "Os nomes das variáveis precisam corresponder ao modelo treinado. "
        "A entrada é reordenada para seguir a ordem das variáveis do treino."
    )

# =========================================================
# RUN PREDICTIONS
# =========================================================
section_heading("4. Gerar predições")

if missing_cells:
    st.warning(
        "Este dataset tem valores ausentes. A predição pode falhar se "
        "o pipeline do modelo salvo não souber tratá-los."
    )

if st.button(
    "🚀 Gerar predições",
    type="primary",
    width="stretch",
    disabled=bool(missing_features),
    key="page7_predict_button",
):
    try:
        prediction_input = df[predictor.feature_names].copy()

        with st.spinner("Executando as predições do modelo..."):
            predictions = predictor.predict(prediction_input)

        if len(predictions) != len(df):
            raise ValueError(
                "O número de predições não corresponde ao número de linhas de entrada."
            )

        result = prediction_input.copy()
        result["Predição"] = predictions

        # If available, attach class probabilities/confidence for classifiers.
        # This is optional; some estimators do not support predict_proba.
        probability_note = None
        try:
            model_object = getattr(predictor, "model", None)
            if model_object is not None and hasattr(model_object, "predict_proba"):
                probabilities = model_object.predict_proba(prediction_input)
                classes = getattr(model_object, "classes_", None)
                if probabilities is not None and len(probabilities) == len(result):
                    max_probability = probabilities.max(axis=1)
                    result["Confiança da Predição (%)"] = (
                        max_probability * 100
                    ).round(2)
                    if classes is not None and probabilities.shape[1] <= 20:
                        for index, class_name in enumerate(classes):
                            result[f"Probabilidade - {class_name} (%)"] = (
                                probabilities[:, index] * 100
                            ).round(2)
                    probability_note = (
                        "As colunas de probabilidade foram adicionadas com o método "
                        "predict_proba do modelo. São scores do modelo, não garantias."
                    )
        except Exception as probability_exc:
            probability_note = (
                "A predição foi concluída, mas os scores de probabilidade "
                f"opcionais não estavam disponíveis: {probability_exc}"
            )

        metadata = {
            "input_signature": input_signature,
            "model": selected_model,
            "dataset": uploaded_file.name,
            "rows": len(result),
            "columns": len(prediction_input.columns),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "problem_type": getattr(predictor, "problem_type", "Desconhecido"),
            "probability_note": probability_note,
        }
        st.session_state[RESULTS_KEY] = result
        st.session_state[META_KEY] = metadata
        st.success("Execução de predição concluída.")
        st.rerun()

    except Exception as exc:
        st.error("Não foi possível concluir a predição.")
        with st.expander("Detalhes técnicos do erro"):
            st.code(str(exc))

# =========================================================
# RESULTS
# =========================================================
stored_result = st.session_state.get(RESULTS_KEY)
metadata = st.session_state.get(META_KEY)

if stored_result is not None and metadata is not None:
    if metadata.get("input_signature") != input_signature:
        st.info("O resultado anterior pertence a outra entrada. Gere uma nova execução.")
    else:
        result = stored_result.copy()
        prediction_series = result["Predição"]
        numeric_predictions = pd.to_numeric(prediction_series, errors="coerce")
        is_numeric = prediction_is_numeric(prediction_series)

        st.divider()
        section_heading("5. Visão geral das predições")

        if is_numeric:
            valid_values = numeric_predictions.dropna()
            a, b, c, d = st.columns(4)
            a.metric("Registros previstos", f"{len(result):,}")
            b.metric("Predição média", format_number(valid_values.mean()) if not valid_values.empty else "N/A")
            c.metric("Mínimo", format_number(valid_values.min()) if not valid_values.empty else "N/A")
            d.metric("Máximo", format_number(valid_values.max()) if not valid_values.empty else "N/A")

            if not valid_values.empty:
                spread = valid_values.max() - valid_values.min()
                st.caption(
                    f"Amplitude: {format_number(spread)} · Desvio padrão: "
                    f"{format_number(valid_values.std())}"
                )
        else:
            class_counts = prediction_series.astype(str).value_counts()
            a, b, c = st.columns(3)
            a.metric("Registros previstos", f"{len(result):,}")
            b.metric("Classes previstas distintas", f"{len(class_counts):,}")
            c.metric(
                "Classe mais frequente",
                str(class_counts.index[0])[:40] if not class_counts.empty else "N/A",
            )
            st.dataframe(
                class_counts.rename_axis("Classe prevista")
                .reset_index(name="Registros"),
                width="stretch",
                hide_index=True,
            )

        if metadata.get("probability_note"):
            st.caption(metadata["probability_note"])

        # Optional actual-vs-predicted evaluation, if user supplies actual target values.
        with st.expander("Opcional: comparar predições com valores reais"):
            actual_col = st.selectbox(
                "Escolha uma coluna com os valores reais do alvo",
                options=["(Não informado)"] + list(df.columns),
                key="page7_actual_target_col",
            )
            if actual_col != "(Não informado)":
                actual = df[actual_col].reset_index(drop=True)
                predicted = result["Predição"].reset_index(drop=True)
                compare = pd.DataFrame({"Real": actual, "Previsto": predicted})
                if prediction_is_numeric(actual) and prediction_is_numeric(predicted):
                    compare["Real"] = pd.to_numeric(compare["Real"], errors="coerce")
                    compare["Previsto"] = pd.to_numeric(compare["Previsto"], errors="coerce")
                    compare = compare.dropna()
                    if not compare.empty:
                        mae = (compare["Real"] - compare["Previsto"]).abs().mean()
                        rmse = (((compare["Real"] - compare["Previsto"]) ** 2).mean()) ** 0.5
                        m1, m2, m3 = st.columns(3)
                        m1.metric("Linhas comparadas", f"{len(compare):,}")
                        m2.metric("MAE", format_number(mae))
                        m3.metric("RMSE", format_number(rmse))
                        st.caption("Estas métricas só fazem sentido se a coluna selecionada for o alvo real dessas mesmas linhas.")
                else:
                    compare["Acertou?"] = compare["Real"].astype(str) == compare["Previsto"].astype(str)
                    m1, m2 = st.columns(2)
                    m1.metric("Linhas comparadas", f"{len(compare):,}")
                    m2.metric("Acurácia nas linhas informadas", f"{compare['Acertou?'].mean() * 100:.2f}%")
                st.dataframe(compare, width="stretch", hide_index=True)

        # Search/filter/sort tools
        st.divider()
        section_heading("6. Explorar resultados")

        search_col, filter_col, sort_col = st.columns([1.2, 1, 1])
        with search_col:
            search_text = st.text_input(
                "Buscar nos resultados",
                placeholder="Buscar em todas as colunas...",
                key="page7_result_search",
            )
        with filter_col:
            prediction_options = sorted(prediction_series.astype(str).unique().tolist())
            selected_predictions = st.multiselect(
                "Filtrar valores previstos",
                options=prediction_options,
                default=prediction_options,
                key="page7_prediction_filter",
            )
        with sort_col:
            sort_column = st.selectbox(
                "Ordenar resultados por",
                options=list(result.columns),
                key="page7_sort_column",
            )

        sort_ascending = st.checkbox(
            "Ordem crescente",
            value=True,
            key="page7_sort_ascending",
        )

        filtered_result = result[
            result["Predição"].astype(str).isin(selected_predictions)
        ].copy()

        if search_text.strip():
            search_mask = filtered_result.astype(str).apply(
                lambda col: col.str.contains(
                    search_text.strip(), case=False, regex=False, na=False
                )
            ).any(axis=1)
            filtered_result = filtered_result[search_mask]

        try:
            filtered_result = filtered_result.sort_values(
                by=sort_column, ascending=sort_ascending, kind="stable"
            )
        except (TypeError, ValueError):
            st.info("Alguns valores desta coluna não podem ser ordenados juntos.")

        st.caption(f"Exibindo {len(filtered_result):,} de {len(result):,} registros.")
        st.dataframe(filtered_result, width="stretch", hide_index=True)

        # Charts
        st.divider()
        section_heading("7. Visualizações das predições")
        chart_tab1, chart_tab2, chart_tab3 = st.tabs(
            ["Distribuição", "Contagens", "Relação com variáveis"]
        )

        if filtered_result.empty:
            st.info("Nenhum resultado corresponde à busca e aos filtros atuais.")
        else:
            with chart_tab1:
                try:
                    if is_numeric:
                        plot_values = pd.to_numeric(
                            filtered_result["Predição"], errors="coerce"
                        ).dropna()
                        if not plot_values.empty:
                            fig = px.histogram(
                                x=plot_values,
                                nbins=30,
                                title="Distribuição dos valores previstos",
                                labels={"x": "Predição", "y": "Registros"},
                            )
                            st.plotly_chart(fig, width="stretch")
                        else:
                            st.info("Não há predições numéricas para plotar.")
                    else:
                        counts = filtered_result["Predição"].astype(str).value_counts().rename_axis("Classe").reset_index(name="Registros")
                        fig = px.pie(
                            counts, names="Classe", values="Registros",
                            title="Participação das classes previstas", hole=0.35
                        )
                        st.plotly_chart(fig, width="stretch")
                except Exception as exc:
                    st.info(f"Não foi possível criar o gráfico de distribuição: {exc}")

            with chart_tab2:
                try:
                    if is_numeric:
                        counts = pd.to_numeric(
                            filtered_result["Predição"], errors="coerce"
                        ).dropna().value_counts().sort_index().rename_axis("Predição").reset_index(name="Registros")
                    else:
                        counts = filtered_result["Predição"].astype(str).value_counts().rename_axis("Predição").reset_index(name="Registros")
                    fig = px.bar(
                        counts, x="Predição", y="Registros",
                        title="Contagem de predições"
                    )
                    st.plotly_chart(fig, width="stretch")
                except Exception as exc:
                    st.info(f"Não foi possível criar o gráfico de contagens: {exc}")

            with chart_tab3:
                candidate_features = [
                    col for col in predictor.feature_names
                    if col in filtered_result.columns
                    and pd.api.types.is_numeric_dtype(filtered_result[col])
                ]
                if candidate_features and is_numeric:
                    x_feature = st.selectbox(
                        "Variável numérica para o gráfico de relação",
                        options=candidate_features,
                        key="page7_relationship_feature",
                    )
                    relationship = filtered_result[[x_feature, "Predição"]].copy()
                    relationship["Predição"] = pd.to_numeric(
                        relationship["Predição"], errors="coerce"
                    )
                    relationship = relationship.dropna()
                    if not relationship.empty:
                        fig = px.scatter(
                            relationship, x=x_feature, y="Predição",
                            title=f"{x_feature} vs valor previsto",
                            trendline=None,
                        )
                        st.plotly_chart(fig, width="stretch")
                    else:
                        st.info("Não há valores numéricos utilizáveis para esta relação.")
                else:
                    st.info(
                        "O gráfico de relação fica disponível quando o resultado inclui "
                        "uma variável de entrada numérica e predições numéricas."
                    )

        # Export
        st.divider()
        section_heading("8. Exportar resultados")
        export_all, export_filtered = st.columns(2)
        with export_all:
            st.download_button(
                "Baixar todas as predições",
                data=safe_csv_bytes(result),
                file_name="NexDecision_All_Predictions.csv",
                mime="text/csv",
                width="stretch",
                key="page7_download_all",
            )
        with export_filtered:
            st.download_button(
                "Baixar resultados filtrados",
                data=safe_csv_bytes(filtered_result),
                file_name="NexDecision_Filtered_Predictions.csv",
                mime="text/csv",
                width="stretch",
                key="page7_download_filtered",
            )

        with st.expander("Exportador CSV avançado"):
            try:
                exporter = PredictionExporter()
                export_filename = exporter.export_csv(
                    result, filename="Predictions.csv"
                )
                with open(export_filename, "rb") as export_file:
                    st.download_button(
                        "Baixar pelo Prediction Exporter",
                        data=export_file.read(),
                        file_name="Predictions.csv",
                        mime="text/csv",
                        key="page7_exporter_download",
                    )
            except Exception as exc:
                st.caption(f"Exportador opcional indisponível: {exc}")

        # History
        st.divider()
        section_heading("9. Histórico de predições")
        if st.button(
            "Salvar esta execução no histórico de predições",
            key="page7_save_history",
        ):
            try:
                database = Database()
                database.save_prediction(
                    metadata["model"], metadata["dataset"], metadata["rows"]
                )
                st.success("Execução de predição salva no histórico.")
            except Exception as exc:
                st.warning(f"Não foi possível salvar o histórico; os resultados continuam disponíveis. Detalhes: {exc}")

        try:
            history = Database().get_predictions()
            if history is not None:
                st.dataframe(
                    history if isinstance(history, pd.DataFrame) else pd.DataFrame(history),
                    width="stretch",
                    hide_index=True,
                )
        except Exception:
            st.caption("O histórico de predições salvo está indisponível no momento.")

        with st.expander("Informações da execução de predição"):
            st.write(f"**Modelo:** {metadata['model']}")
            st.write(f"**Dataset:** {metadata['dataset']}")
            st.write(f"**Linhas processadas:** {metadata['rows']:,}")
            st.write(f"**Qtd. de variáveis:** {metadata['columns']:,}")
            st.write(f"**Horário da execução:** {metadata['timestamp']}")
            st.write(f"**Tipo de problema:** {metadata['problem_type']}")

        ai_insight(
            "Predições são estimativas do modelo, não garantias. Verifique a "
            "qualidade dos dados e a compatibilidade das variáveis e, quando "
            "possível, compare os resultados com desfechos conhecidos antes de "
            "tomar decisões reais."
        )

page_footer()

# =========================================================
# PREVIOUS / NEXT PAGE NAVIGATION
# Keep this at the very bottom of app/pages/7_Prediction.py.
# =========================================================
st.divider()
nav_previous, nav_spacer, nav_next = st.columns([1, 2, 1])

with nav_previous:
    if st.button(
        "⬅️ Anterior: Previsão de Negócios",
        key="page7_previous_navigation",
        use_container_width=True,
    ):
        st.switch_page("pages/6_Business_Forecasting.py")

with nav_next:
    if st.button(
        "Próximo ➡️",
        key="page7_next_navigation",
        use_container_width=True,
    ):
        st.switch_page("pages/9_Interactive_Dashboard.py")
