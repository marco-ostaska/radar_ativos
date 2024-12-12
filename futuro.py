import requests
from bs4 import BeautifulSoup

URL = "https://br.advfn.com/bolsa-de-valores/bmf/DI1F27/cotacao"

def obter_dados_precos():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }
    try:
        # Faz a requisição com cabeçalho de User-Agent
        response = requests.get(URL, headers=headers)
        response.raise_for_status()  # Verifica se a resposta foi bem-sucedida

        # Parsing do HTML
        soup = BeautifulSoup(response.content, "html.parser")

        # Seleciona o bloco que contém o preço
        price_block = soup.find("div", class_="price-block", attrs={"data-asc-symbol": "BMF^DI1F27"})

        if price_block:
            preco = price_block.text.strip()  # Extrai o valor do preço
            preco_float = float(preco.replace(',', '.'))
            return {"preco_atual": preco_float}
        else:
            print("Bloco de preço não encontrado!")
            return None
    except Exception as e:
        print("Erro ao acessar a página:", e)
        return None

# Executa o script
dados = obter_dados_precos()

if dados:
    print("Dados do contrato DI1F27:")
    print(dados)
else:
    print("Não foi possível obter os dados.")
