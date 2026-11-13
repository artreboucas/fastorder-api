FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Aplica correções de segurança do sistema operacional (alvo do Trivy)
RUN apt-get update \
    && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar requirements antes do código aproveita o cache de camadas
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY app.py .

# Boa prática: não executar como root
RUN useradd --no-create-home --shell /usr/sbin/nologin appuser
USER appuser

EXPOSE 5000

# A Feature Flag nasce desligada; é ligada apenas por variável de ambiente
ENV FEATURE_DESCONTO_PROMO=false

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
