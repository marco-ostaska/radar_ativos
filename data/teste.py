import asyncio
import json
from motor.motor_asyncio import AsyncIOMotorClient

CAMINHO_JSON = "bc.json"

async def importar_bc():
    uri = "mongodb://admin:senha123@localhost:27017"
    client = AsyncIOMotorClient(uri)
    db = client["radar_db"]
    colecao = db["indicadores"]

    with open(CAMINHO_JSON, "r", encoding="utf-8") as f:
        dados = json.load(f)

    # Define a chave fixa do documento
    dados["_id"] = "bc"

    # Atualiza o documento com _id = "bc", ou cria se não existir
    resultado = await colecao.replace_one(
        {"_id": "bc"},  # filtro
        dados,          # novo conteúdo inteiro
        upsert=True     # cria se não existir
    )

    if resultado.matched_count > 0:
        print("Documento 'bc' atualizado.")
    else:
        print("Documento 'bc' inserido.")

asyncio.run(importar_bc())
