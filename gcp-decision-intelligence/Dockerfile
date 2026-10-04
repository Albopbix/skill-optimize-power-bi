FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8080

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

# Usuário sem privilégios; a pasta /app precisa ser gravável para
# saved_models/ (cache), relatórios PDF e CSVs de predição temporários.
RUN useradd --create-home appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8080

CMD ["sh", "-c", "streamlit run app/app.py --server.port=${PORT} --server.address=0.0.0.0"]
