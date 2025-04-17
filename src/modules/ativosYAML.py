import streamlit as st
import yaml
from pathlib import Path
import requests

base_dir = Path(__file__).resolve().parents[2]
ativo_arq = base_dir / "data" / "ativos.yml"

def load_data():
    with open(ativo_arq, "r") as file:
        return yaml.safe_load(file)

def save_data(data):
    with open(ativo_arq, "w") as file:
        yaml.safe_dump(data, file)

def add_ativo(ticker, categoria):
    data = load_data()
    if categoria not in data:
        data[categoria] = {"spread": 0, "tickers": []}

    if any(item["ticker"] == ticker for item in data[categoria]["tickers"]):
        return False

    data[categoria]["tickers"].append({"ticker": ticker})
    data[categoria]["tickers"] = sorted(
        {item["ticker"]: item for item in data[categoria]["tickers"]}.values(),
        key=lambda x: x["ticker"]
    )

    save_data(data)
    return True

def remove_ativo(ticker, categoria):
    data = load_data()
    if categoria in data:
        original_len = len(data[categoria]["tickers"])
        data[categoria]["tickers"] = [item for item in data[categoria]["tickers"] if item["ticker"] != ticker]
        if len(data[categoria]["tickers"]) != original_len:
            save_data(data)
            return True
    return False

def montar_add():
    st.title("Adicionar Ativos")
    with st.form(key="add_ativo_form"):
        ticker = st.text_input("Ticker")
        categoria = st.selectbox("Categoria", ["agro", "infra", "shopping", "logistica", "acoes", "hibrido", "papel"])
        submit = st.form_submit_button("Adicionar Ativo")

    if submit:
        if add_ativo(ticker, categoria):
            st.success(f"Ativo {ticker} adicionado à categoria {categoria}.")
        else:
            st.error(f"Ativo {ticker} já existe na categoria {categoria}.")

    st.header("Lista de Ativos")
    st.write(load_data())

def montar_remove():
    st.title("Remover Ativos")
    with st.form(key="remove_ativo_form"):
        ticker = st.text_input("Ticker")
        categoria = st.selectbox("Categoria", ["agro", "infra", "shopping", "logistica", "acoes", "hibrido", "papel"])
        submit = st.form_submit_button("Remover Ativo")

    if submit:
        if remove_ativo(ticker, categoria):
            st.success(f"Ativo {ticker} removido da categoria {categoria}.")
        else:
            st.error(f"Ativo {ticker} não encontrado na categoria {categoria}.")

    st.header("Lista de Ativos")
    st.write(load_data())

def main():
    st.sidebar.title("Menu")
    opcao = st.sidebar.selectbox("Escolha uma opção", ["Adicionar Ativo", "Remover Ativo"])
    if opcao == "Adicionar Ativo":
        montar_add()
    elif opcao == "Remover Ativo":
        montar_remove()

if __name__ == "__main__":
    main()
