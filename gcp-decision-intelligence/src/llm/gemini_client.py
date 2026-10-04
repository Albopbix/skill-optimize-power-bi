"""
Cliente Gemini via Vertex AI para o Copilot e o AI Chat.

Ativado quando ``GEMINI_ENABLED=true``. A autenticação usa as Application
Default Credentials (no Cloud Run, a service account do serviço; localmente,
``gcloud auth application-default login``).

Variáveis de ambiente:

    GEMINI_ENABLED          true/false (padrão false -> motor de regras original)
    GOOGLE_CLOUD_PROJECT    projeto do Vertex AI
    GOOGLE_CLOUD_LOCATION   região do Vertex AI (padrão "global")
    GEMINI_MODEL            modelo (padrão gemini-3.5-flash)
    GEMINI_SAMPLE_ROWS      linhas de amostra enviadas ao modelo (padrão 5;
                            0 = envia só esquema e estatísticas agregadas)
    GEMINI_LANGUAGE         idioma das respostas (padrão "the same language
                            as the user's question")

O que vai para o modelo: nomes e tipos das colunas, contagem de nulos,
estatísticas descritivas e, se GEMINI_SAMPLE_ROWS > 0, algumas linhas de
amostra. O dataset completo nunca é enviado.
"""

import os
import threading

import numpy as np
import pandas as pd


DEFAULT_MODEL = "gemini-3.5-flash"

MAX_COLUMNS_IN_CONTEXT = 60
MAX_CATEGORY_VALUES = 8
MAX_CELL_CHARS = 80
MAX_HISTORY_TURNS = 10

SYSTEM_INSTRUCTION = """\
You are Nex Decision AI, a business intelligence copilot.
You answer questions about the user's active dataset using ONLY the dataset
profile provided (schema, statistics, sample rows). Rules:
- Ground every number in the profile. Never invent values, columns or rows.
- If the profile is not enough to answer exactly (e.g. it needs the full
  data), say so and explain which analysis in the app (AutoML, Forecasting,
  Anomaly Detection, Interactive Dashboard) would answer it.
- Be concise and business-oriented: findings, risks, opportunities and
  concrete next actions. Use short Markdown (bullets, bold), no tables wider
  than 5 columns.
- Answer in {language}.
"""

_client_lock = threading.Lock()
_client = None


def is_enabled():

    return os.getenv("GEMINI_ENABLED", "false").strip().lower() in (
        "1", "true", "yes", "on"
    )


def model_name():

    return os.getenv("GEMINI_MODEL", DEFAULT_MODEL)


def _get_client():

    global _client

    with _client_lock:

        if _client is None:

            from google import genai

            _client = genai.Client(
                vertexai=True,
                project=os.getenv("GOOGLE_CLOUD_PROJECT") or None,
                location=os.getenv("GOOGLE_CLOUD_LOCATION", "global"),
            )

        return _client


def _truncate(value):

    text = str(value)

    if len(text) > MAX_CELL_CHARS:
        return text[:MAX_CELL_CHARS] + "…"

    return text


def build_dataset_context(df):

    """Resumo compacto do dataset para o prompt (sem enviar os dados brutos)."""

    lines = [
        f"Rows: {len(df):,}",
        f"Columns: {len(df.columns)}",
        f"Total missing cells: {int(df.isnull().sum().sum()):,}",
        f"Duplicate rows: {int(df.duplicated().sum()):,}",
        "",
        "Columns (name | dtype | missing | unique | profile):",
    ]

    columns = list(df.columns)[:MAX_COLUMNS_IN_CONTEXT]

    for column in columns:

        series = df[column]
        missing = int(series.isnull().sum())
        unique = int(series.nunique(dropna=True))

        if pd.api.types.is_numeric_dtype(series) and not pd.api.types.is_bool_dtype(series):

            stats = series.describe()
            profile = (
                f"mean={stats.get('mean', float('nan')):.4g}, "
                f"std={stats.get('std', float('nan')):.4g}, "
                f"min={stats.get('min', float('nan')):.4g}, "
                f"p50={stats.get('50%', float('nan')):.4g}, "
                f"max={stats.get('max', float('nan')):.4g}"
            )

        elif pd.api.types.is_datetime64_any_dtype(series):

            profile = f"range={series.min()} → {series.max()}"

        else:

            top = series.astype(str).value_counts().head(MAX_CATEGORY_VALUES)
            profile = "top=" + ", ".join(
                f"{_truncate(k)} ({v})" for k, v in top.items()
            )

        lines.append(
            f"- {column} | {series.dtype} | {missing} | {unique} | {profile}"
        )

    if len(df.columns) > MAX_COLUMNS_IN_CONTEXT:
        lines.append(
            f"(+{len(df.columns) - MAX_COLUMNS_IN_CONTEXT} more columns omitted)"
        )

    numeric = df[columns].select_dtypes(include="number")

    if numeric.shape[1] >= 2:

        corr = numeric.corr().abs()
        upper = np.triu(np.ones(corr.shape, dtype=bool), k=1)
        pairs = (
            corr.where(upper)
            .stack()
            .dropna()
            .sort_values(ascending=False)
            .head(5)
        )

        if not pairs.empty:
            lines.append("")
            lines.append("Strongest numeric correlations (|r|):")
            for (a, b), r in pairs.items():
                lines.append(f"- {a} ~ {b}: {r:.2f}")

    sample_rows = int(os.getenv("GEMINI_SAMPLE_ROWS", "5"))

    if sample_rows > 0 and len(df):

        sample = df[columns].head(sample_rows).map(_truncate)
        lines.append("")
        lines.append(f"Sample rows (first {len(sample)}):")
        lines.append(sample.to_csv(index=False))

    return "\n".join(lines)


def ask(question, df, history=None):

    """
    Pergunta ao Gemini usando o perfil do dataset como contexto.

    ``history`` é uma lista de tuplas (remetente, mensagem) no formato do
    AI Chat, onde remetente "You" é o usuário e qualquer outro é o modelo.
    """

    from google.genai import types

    language = os.getenv(
        "GEMINI_LANGUAGE",
        "the same language as the user's question"
    )

    contents = []

    for sender, message in (history or [])[-MAX_HISTORY_TURNS * 2:]:

        contents.append(types.Content(
            role="user" if sender == "You" else "model",
            parts=[types.Part.from_text(text=str(message))],
        ))

    prompt = (
        "DATASET PROFILE\n"
        "===============\n"
        f"{build_dataset_context(df)}\n\n"
        "QUESTION\n"
        "========\n"
        f"{question}"
    )

    contents.append(types.Content(
        role="user",
        parts=[types.Part.from_text(text=prompt)],
    ))

    response = _get_client().models.generate_content(
        model=model_name(),
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION.format(language=language),
            temperature=0.2,
            max_output_tokens=2048,
        ),
    )

    text = (response.text or "").strip()

    if not text:
        raise RuntimeError("Gemini returned an empty response.")

    return text
