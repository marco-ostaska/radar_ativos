import os
import json
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, Query
from modules.investidor10 import FII as I10FII
import modules.fii as fii
import modules.scoreFII as scoreFII
import modules.acoes as acoes
import modules.score as score
import yaml
from pathlib import Path
from modules.bancoCentral import SELIC, IPCA

# Extensões para preencher propriedades ausentes na classe acao
setattr(acoes.acao, "lucro_liquido", property(lambda self: self.acao.info.get("netIncomeToCommon")))
setattr(acoes.acao, "valor_mercado", property(lambda self: self.acao.info.get("marketCap")))
setattr(acoes.acao, "vpa", property(lambda self: self.acao.info.get("bookValue")))
setattr(acoes.acao, "lpa", property(lambda self: self.acao.info.get("trailingEps")))

app = FastAPI()

base_dir = Path(__file__).resolve().parents[1]  # sobe dois níveis
INDICES_CACHE_FILE = base_dir / 'data' / 'bc.json'
CACHE_DIAS_VALIDO = 30

def risco_operacional(tipo):
    tipos = {"shopping": 4, "logistica": 2, "papel": 8, "hibrido": 6}
    return 10 if tipo not in tipos else tipos[tipo]

def get_indices():
    if os.path.exists(INDICES_CACHE_FILE):
        with open(INDICES_CACHE_FILE) as f:
            data = json.load(f)
            try:
                data_date = datetime.strptime(data['date'], "%Y-%m-%d")
                if datetime.now() - data_date < timedelta(days=CACHE_DIAS_VALIDO):
                    return data
            except:
                pass

    try:
        selic = SELIC(5)
        ipca = IPCA(5)
        ipc_a = IPCA(1)

        data = {
            'date': datetime.now().strftime("%Y-%m-%d"),
            'selic': selic.media_ganho_real,
            'selic_atual': selic.atual,
            'ipca': ipca.media_ganho_real,
            'ipca_media5': ipca.media_anual,
            'ipca_atual': ipc_a.media_anual
        }

        with open(INDICES_CACHE_FILE, "w") as f:
            json.dump(data, f)

        return data
    except Exception as e:
        raise RuntimeError(f"Erro ao buscar índices: {str(e)}")

def melhor_indice():
    indices = get_indices()
    return max(indices['selic'], indices['ipca'])

@app.get("/indices")
def get_indices_endpoint(force: bool = Query(False, description="Força atualização dos dados")):
    if force and os.path.exists(INDICES_CACHE_FILE):
        os.remove(INDICES_CACHE_FILE)
    try:
        return get_indices()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
            "historico_dividendos": {k: round(v, 4) for k, v in fi.historico_dividendos.items()},
            "raw_dividends": fi.dividends.tail(12).to_dict(),
            "cotas_necessarias_para_1000_mensais": cotas_necessarias,
            "investimento_necessario_para_1000_mensais": investimento_necessario
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/acoes/detalhado")
def obter_detalhes_acao(
    ticker: str = Query(..., description="Ticker da ação, ex: ITSA4")
):
    try:
        ticker = ticker.upper()
        if not ticker.endswith(".SA"):
            ticker += ".SA"

        acao_obj = acoes.acao(ticker)
        indice_base = melhor_indice()
        indices = get_indices()

        dy_estimado = (acao_obj.dy_estimado * 100) if acao_obj.dy_estimado else 0
        teto_dy_valor = (acao_obj.dy_estimado * acao_obj.cotacao) / (indice_base / 100) if acao_obj.dy_estimado else 0
        real = dy_estimado - indices['ipca_atual']
        base = acao_obj.teto_cotacao_lucro if acao_obj.teto_cotacao_lucro else teto_dy_valor
        potencial = round((((base - acao_obj.cotacao) / acao_obj.cotacao) * 100), 2)
        nota_risco = 11 - acao_obj.risco_geral
        score_valor = score.evaluate_company(acao_obj.acao, indice_base)
        cota_necessaria = round(1000 / ((acao_obj.dy_estimado * acao_obj.cotacao) / 12), 0) if acao_obj.dy_estimado else 0
        investimento_necessario = cota_necessaria * acao_obj.cotacao

        return {
            "ticker": ticker.replace(".SA", ""),
            "cotacao": round(acao_obj.cotacao, 2),
            "lucro_liquido": acao_obj.lucro_liquido,
            "valor_mercado": acao_obj.valor_mercado,
            "vpa": acao_obj.vpa,
            "lpa": acao_obj.lpa,
            "roe": round(acao_obj.roe, 2) if acao_obj.roe else None,
            "dy_estimado": round(dy_estimado, 2),
            "valor_teto_por_dy": round(teto_dy_valor, 2),
            "rendimento_real": round(real, 2),
            "potencial": potencial,
            "earning_yield": round(acao_obj.earning_yield, 2),
            "nota_risco": round(nota_risco, 2),
            "score": round(score_valor, 2),
            "margem_liquida": acao_obj.margem_liquida,
            "liquidez_corrente": acao_obj.liquidez_corrente,
            "divida_ebitda": acao_obj.div_ebitda,
            "receita": acao_obj.receita,
            "lucro": acao_obj.lucro,
            "free_float": acao_obj.free_float,
            "pl": acao_obj.pl,
            "cotas_necessarias_para_1000_mensais": cota_necessaria,
            "investimento_necessario_para_1000_mensais": round(investimento_necessario, 2)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/acoes/radar")
def obter_dados_acao(
    ticker: str = Query(..., description="Ticker da ação, ex: ITSA4")
):
    try:
        ticker = ticker.upper()
        if not ticker.endswith(".SA"):
            ticker += ".SA"

        indice_base = melhor_indice()
        indices = get_indices()

        acao_obj = acoes.acao(ticker)

        dy_estimado = (acao_obj.dy_estimado * 100) if acao_obj.dy_estimado else 0
        teto_dy_valor = (acao_obj.dy_estimado * acao_obj.cotacao) / (indice_base / 100) if acao_obj.dy_estimado else 0
        rf_real = (indices['selic_atual'] - (indices['selic_atual'] * 0.15)) - indices['ipca_atual']
        real = dy_estimado - indices['ipca_atual']
        base = acao_obj.teto_cotacao_lucro if acao_obj.teto_cotacao_lucro else teto_dy_valor
        potencial = round((((base - acao_obj.cotacao) / acao_obj.cotacao) * 100), 2)
        nota_risco = 11 - acao_obj.risco_geral
        score_valor = score.evaluate_company(acao_obj.acao, indice_base)

        return {
            "ticker": ticker.replace(".SA", ""),
            "cotacao": round(acao_obj.cotacao, 2),
            "teto_por_lucro": round(acao_obj.teto_cotacao_lucro, 2) if acao_obj.teto_cotacao_lucro else None,
            "dy_estimado": round(dy_estimado, 2),
            "valor_teto_por_dy": round(teto_dy_valor, 2),
            "rendimento_real": round(real, 2),
            "potencial": potencial,
            "earning_yield": round(acao_obj.earning_yield, 2),
            "nota_risco": round(nota_risco, 2),
            "score": round(score_valor, 2)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
