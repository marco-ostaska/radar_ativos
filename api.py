from fastapi import FastAPI, HTTPException, Query
from investidor10 import FII as I10FII
import fii
import scoreFII
import yaml
from bancoCentral import SELIC, IPCA
from datetime import datetime
import time

app = FastAPI()

# Cache dos índices
_indices_cache = None
_cache_timestamp = 0
_CACHE_TTL = 60 * 60 * 24  # 24 horas


def risco_operacional(tipo):
    if tipo == "papel":
        return 8
    if tipo == "hibrido":
        return 6
    if tipo == "shopping":
        return 4
    if tipo == "logistica":
        return 2
    return 10


def get_indices():
    global _indices_cache, _cache_timestamp
    now = time.time()

    if _indices_cache and (now - _cache_timestamp) < _CACHE_TTL:
        return _indices_cache

    try:
        selic = SELIC(5)
        ipca = IPCA(5)
        ipc_a = IPCA(1)

        _indices_cache = {
            'selic': selic.media_ganho_real,
            'selic_atual': selic.atual,
            'ipca': ipca.media_ganho_real,
            'ipca_media5': ipca.media_anual,
            'ipca_atual': ipc_a.media_anual
        }
        _cache_timestamp = now
        return _indices_cache
    except Exception as e:
        raise RuntimeError(f"Erro ao buscar índices: {str(e)}")


def melhor_indice():
    indices = get_indices()
    return max(indices['selic'], indices['ipca'])


# ----------------------------- ENDPOINTS -----------------------------

@app.get("/investidor10/fii/{ticker}")
def get_fii_info(ticker: str):
    try:
        ativo = I10FII(ticker)
        return {
            "ticker": ativo.ticker,
            "cotacao": ativo.cotacao,
            "pvp": ativo.pvp,
            "div_yield": ativo.div_yield,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/fii/radar")
def obter_dados_fii(
    ticker: str = Query(..., description="Ticker do FII, ex: HGLG11"),
    tipo: str = Query(..., description="Tipo do fundo: shopping, logistica, papel, hibrido, fiagro ou infra")
):
    tipos_validos = ["shopping", "logistica", "papel", "hibrido", "fiagro", "infra"]
    if tipo not in tipos_validos:
        raise HTTPException(status_code=400, detail=f"Tipo inválido. Use um de: {', '.join(tipos_validos)}")

    try:
        with open("ativos.yml", "r") as file:
            data = yaml.safe_load(file)

        tipo_data = data.get(tipo)
        if not tipo_data:
            raise HTTPException(status_code=404, detail=f"Tipo '{tipo}' não encontrado no YAML.")

        spread = tipo_data["spread"]
        indice_base = melhor_indice()
        indices = get_indices()

        ticker = ticker.upper()
        if not ticker.endswith(".SA"):
            ticker += ".SA"

        fi = fii.FII(ticker)

        spread_total = spread + indice_base
        dy_estimado = (fi.dividendo_estimado * 100) / fi.cotacao
        teto_div = fi.dividendo_estimado / spread_total * 100
        rf_real = (indices['selic_atual'] - (indices['selic_atual'] * 0.15)) - indices['ipca_atual']
        real = dy_estimado - indices['ipca_atual']
        pot = round(((teto_div - fi.cotacao) / fi.cotacao) * 100, 2)
        risco = round(11 - fi.overall_risk(risco_operacional(tipo)), 1)
        nota = scoreFII.evaluate_fii(fi, indice_base)

        return {
            "ticker": fi.ticker.split(".")[0],
            "cotacao": round(fi.cotacao, 2),
            "vpa": round(fi.vpa, 2),
            "teto_div": round(teto_div, 2),
            "dy_estimado": round(dy_estimado, 2),
            "rendimento_real": round(real, 2),
            "potencial": pot,
            "nota_risco": risco,
            "score": nota,
            "indice_base": indice_base,
            "spread_usado": spread_total
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/fii/detalhado")
def get_fii_detalhado(
    ticker: str = Query(..., description="Ticker do FII, ex: HGLG11"),
    tipo: str = Query(..., description="Tipo do fundo: shopping, logistica, papel, hibrido, fiagro ou infra")
):
    tipos_validos = ["shopping", "logistica", "papel", "hibrido", "fiagro", "infra"]
    if tipo not in tipos_validos:
        raise HTTPException(status_code=400, detail=f"Tipo inválido. Use um de: {', '.join(tipos_validos)}")

    try:
        with open("ativos.yml", "r") as file:
            data = yaml.safe_load(file)

        tipo_data = data.get(tipo)
        if not tipo_data:
            raise HTTPException(status_code=404, detail=f"Tipo '{tipo}' não encontrado no YAML.")

        spread = tipo_data["spread"]
        indice_base = melhor_indice()
        indices = get_indices()

        ticker = ticker.upper()
        if not ticker.endswith(".SA"):
            ticker += ".SA"

        fi = fii.FII(ticker)

        spread_total = spread + indice_base
        dy_estimado = (fi.dividendo_estimado * 100) / fi.cotacao
        teto_div = fi.dividendo_estimado / spread_total * 100
        rf_real = (indices['selic_atual'] - (indices['selic_atual'] * 0.15)) - indices['ipca_atual']
        real = dy_estimado - indices['ipca_atual']
        pot = round(((teto_div - fi.cotacao) / fi.cotacao) * 100, 2)
        risco = round(11 - fi.overall_risk(risco_operacional(tipo)), 1)
        nota = scoreFII.evaluate_fii(fi, indice_base)
        cotas_necessarias = round(12000 / fi.dividendo_estimado, 2)
        investimento_necessario = round(cotas_necessarias * fi.cotacao, 2)


        return {
            "ticker": fi.ticker.split(".")[0],
            "cotacao": round(fi.cotacao, 2),
            "valor_patrimonial": round(fi.valor_patrimonial, 2) if fi.valor_patrimonial else None,
            "cotas_emitidas": int(fi.cotas_emitidas) if fi.cotas_emitidas else None,
            "vpa": round(fi.vpa, 2),
            "pvp": round(fi.pvp, 2),
            "dividend_yield": round(fi.dividend_yield * 100, 2),
            "dividendo_estimado": round(fi.dividendo_estimado, 2),
            "dy_estimado": round(dy_estimado, 2),
            "teto_div": round(teto_div, 2),
            "rendimento_real": round(real, 2),
            "potencial": pot,
            "risco_liquidez": fi.risco_liquidez,
            "risco_tamanho": fi.risco_tamanho,
            "risco_preco_volatilidade": fi.risco_preco_volatilidade,
            "risco_rendimento": fi.risco_rendimento,
            "nota_risco": risco,
            "score": nota,
            "indice_base": indice_base,
            "spread_usado": spread_total,
            "historico_dividendos": {
                k: round(v, 4) for k, v in fi.historico_dividendos.items()
            },
            "raw_dividends": fi.dividends.tail(12).to_dict(),
            "cotas_necessarias_para_1000_mensais": cotas_necessarias,
            "investimento_necessario_para_1000_mensais": investimento_necessario

        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.get("/indices")
def get_indices_endpoint(force: bool = Query(False, description="Força atualização dos dados")):
    global _indices_cache, _cache_timestamp

    if force:
        _indices_cache = None
        _cache_timestamp = 0

    try:
        return get_indices()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
