# Usa uma imagem oficial do Python
FROM python:3.11-slim

# Define diretório de trabalho
WORKDIR /app

# Copia requirements e instala dependências
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copia o resto do código para a imagem
COPY . .

# Porta que o Cloud Run vai expor (opcional, apenas documentação)
ENV PORT 8080

# Comando de arranque com expansão de variáveis
CMD exec gunicorn --bind 0.0.0.0:${PORT} app:app --workers 1 --threads 8 --timeout 0
