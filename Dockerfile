# usar imagem python 3.12 slim
FROM python:3.12-slim

# criar diretório de trabalho
WORKDIR /app



# Copiar o arquivo requirements.txt para o container
COPY requirements.txt /app/

# Instalar as dependências
RUN pip install -r requirements.txt

# Copiar arquivos python

COPY *.py /app/

EXPOSE  8501

# Executar  o streamlit na porta 8501
CMD [ "streamlit", "run", "main.py" ]

