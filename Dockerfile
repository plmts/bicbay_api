# Usar uma imagem base do Python
FROM python:3.10-slim

# Definir o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copiar o arquivo de requisitos para o contêiner
COPY requirements.txt .

# Instalar as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo o código da API para o contêiner
COPY . .

# Definir a variável de ambiente para a aplicação Flask
ENV FLASK_APP=app.py

# Expor a porta em que a API vai rodar
EXPOSE 5000

# Comando para iniciar a API
CMD ["flask", "run", "--host=0.0.0.0"]
