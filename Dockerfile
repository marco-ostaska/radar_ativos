# usar imagem python 3.12 slim
FROM python:3.12-slim

# criar diretório de trabalho
WORKDIR /app

# Instalar gcc e outras dependências necessárias

RUN apt update && apt install -y \
    gcc \
    && apt auto-remove -y \
    && rm -rf /var/lib/apt/lists/*


# Copiar o arquivo requirements.txt para o container
COPY requirements.txt ativos.yml /app/

# Instalar as dependências sem cache
RUN pip install --no-cache-dir  --upgrade pip \
    && pip install  --no-cache-dir -r requirements.txt

COPY *.py /app/

EXPOSE  8501

# Executar  o streamlit na porta 8501 and --server.headless true
CMD [ "streamlit", "run", "main.py", "--server.headless", "true" ]

