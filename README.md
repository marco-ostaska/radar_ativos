
# Radar de Ativos - Streamlit App

Este projeto é uma aplicação em Python que utiliza o Streamlit para exibir informações e análises sobre FIIs e ações. A aplicação obtém dados de diversas fontes, processa e exibe essas informações de forma interativa através de uma interface web.


## Disclaimer

Este aplicativo de análise de ativos foi desenvolvido com o objetivo de fornecer informações e análises baseadas em dados disponíveis publicamente. No entanto, **não garantimos a exatidão, completude ou atualidade das informações apresentadas**.

As informações fornecidas neste aplicativo são **apenas para fins educacionais** e **não constituem aconselhamento financeiro ou de investimento**. Qualquer decisão de investimento que você tome com base nas informações fornecidas neste aplicativo é feita por sua própria conta e risco.

Ao usar este aplicativo, você concorda que **não somos responsáveis por quaisquer perdas, danos ou prejuízos** decorrentes de decisões tomadas com base nas informações ou análises apresentadas aqui. **Recomendamos fortemente que você consulte um profissional financeiro qualificado** antes de tomar qualquer decisão de investimento.

O uso deste aplicativo implica na aceitação dos termos deste disclaimer.



## Funcionalidades

- Consulta de ativos FIIs e ações.
- Análise de FIIs e ações com base em indicadores fundamentalistas.
- Exibição de informações gerais, indicadores financeiros e dividendos.
- Radar de FIIs e ações com análise baseada em critérios personalizados.
- Interface interativa para facilitar a navegação e a visualização dos dados.

## Requisitos

- Python 3.12
- Streamlit
- Outras dependências listadas no arquivo `requirements.txt`

## Estrutura do Projeto

- **main.py**: Arquivo principal que inicializa a aplicação e define as funções principais para exibição dos dados.
- **fii_st.py**: Contém as funções relacionadas à exibição de informações detalhadas sobre FIIs.
- **acoes_st.py**: Contém as funções relacionadas à exibição de informações detalhadas sobre ações.
- **Dockerfile**: Arquivo para containerização da aplicação com Docker.

## Como Executar

### Ambiente Local

1. Clone o repositório para sua máquina local.
2. Instale as dependências listadas no arquivo `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```
3. Execute o aplicativo utilizando o Streamlit:
   ```bash
   streamlit run main.py
   ```

### Docker

1. Certifique-se de ter o Docker instalado.
2. Construa a imagem Docker:
   ```bash
   docker build -t radar-ativos .
   ```
3. Execute o container:
   ```bash
   docker run -p 8501:8501 radar-ativos
   ```
4. Acesse a aplicação no navegador através do endereço: `http://localhost:8501`.

## Como Usar

- Utilize a barra lateral para selecionar o tipo de ativo (FII ou Ações) e insira o ticker do ativo que deseja consultar.
- O radar de ativos permite a visualização de diversas informações sobre FIIs e ações, exibindo comparações e notas baseadas em indicadores financeiros.
- A aplicação também exibe análises detalhadas de ativos selecionados, como margem líquida, P/VP, dividendos, entre outros.

## Arquivos

- **main.py**: Controla o fluxo principal da aplicação, incluindo a seleção de ativos e a exibição do radar de ativos.
- **fii_st.py**: Implementa a lógica de processamento e exibição de informações detalhadas sobre FIIs.
- **acoes_st.py**: Implementa a lógica de processamento e exibição de informações detalhadas sobre ações.
- **Dockerfile**: Configura a aplicação para ser executada dentro de um container Docker.

