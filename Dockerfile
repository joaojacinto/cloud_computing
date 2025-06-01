# Usa uma imagem oficial do Python
FROM python:3.11-slim

# Define diretório de trabalho
WORKDIR /app

# Copia requirements e instala dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o resto do código para a imagem
COPY . .

# Porta que o Cloud Run vai expor
ENV PORT 8080

# Indica ao Flask para correr em 0.0.0.0 (acessível publicamente)
ENV FLASK_RUN_HOST 0.0.0.0
ENV FLASK_RUN_PORT 8080

# Comando de arranque
CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:app"]

