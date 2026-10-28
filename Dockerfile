FROM python:3.13-slim
WORKDIR /app
COPY requirements.lock pyproject.toml ./
RUN pip install --no-cache-dir -r requirements.lock
COPY evalgov ./evalgov
COPY README.md ./
RUN pip install --no-cache-dir --no-deps -e . && useradd --create-home --uid 10001 evaluator && mkdir -p /app/var && chown evaluator:evaluator /app/var
USER evaluator
ENV EVALGOV_DB=/app/var/evalgov.sqlite3
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/health', timeout=2)"
CMD ["uvicorn", "evalgov.api:create_app", "--factory", "--host", "0.0.0.0", "--port", "8080"]
