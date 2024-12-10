# usar imagem python 3.12 slim
# FROM python:3.12-slim
FROM python:3.14.0a2-slim-bookworm


# Instalar gcc e outras dependências necessárias

# criar diretório de trabalho
WORKDIR /app

RUN apt update && apt install -y \
    gcc \
    g++ \
    libffi-dev \
   libssl-dev \
    && apt autoremove -y \
    && rm -rf /var/lib/apt/lists/*

# # create user radar gid 1001
# RUN groupadd --gid 1001 radar && \
#     adduser radar --gid 1001 && \
#     chown -R radar:radar /app

# USER radar


# Copiar o arquivo requirements.txt para o container
COPY requirements.txt ativos.yml /app/

# Instalar as dependências sem cache
RUN pip install --no-cache-dir  --upgrade pip \
    && pip install  --no-cache-dir -r requirements.txt

COPY *.py /app/

EXPOSE  8501

# Executar  o streamlit na porta 8501 and --server.headless true
CMD [ "streamlit", "run", "main.py", "--server.headless", "true" ]

