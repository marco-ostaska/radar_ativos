import asyncio
import json
import re
from motor.motor_asyncio import AsyncIOMotorClient
import yaml

# ler arquivo ativos.yml
arquivo = "ativos.yml"
with open(arquivo, "r", encoding="utf-8") as f:
    dados = yaml.safe_load(f)



async def importar_bc(tipo, dado):
    uri = "mongodb://admin:senha123@localhost:27017"
    client = AsyncIOMotorClient(uri)
    db = client["radar_db"]
    colecao = db["indicadores"]

    resultado = await colecao.replace_one(
        {"_id": tipo},  # filtro
        dado,          # novo conteúdo inteiro
        upsert=True     # cria se não existir
    )

    if resultado.matched_count > 0:
        print(f"Documento {tipo} atualizado.")
    else:
        print(f"Documento {tipo} inserido.")


fundos = ["acoes", "fiagro", "hibrido", "infra", "logistica", "papel", "shopping"]

for fundo in fundos:
    # criar obj fundo
    fundo_obj = dados.get(fundo, [])
#    criar lista de tickers
    tickers = [item['ticker'] for item in fundo_obj["tickers"]]

    # Remove duplicatas
    tickers.sort()
    # print(fundo)
    # # Adiciona o ticker na lista de tickers do objeto fundos

    dado = {
        "_id": fundo,
        "spread": fundo_obj["spread"],
        "tickers": tickers
    }

    print(dado)

    asyncio.run(importar_bc(fundo, dado))

