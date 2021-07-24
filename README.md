# Magic Formula
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![GitHub Actions](https://img.shields.io/endpoint.svg?url=https%3A%2F%2Factions-badge.atrox.dev%2Fatrox%2Fsync-dotenv%2Fbadge)](https://actions-badge.atrox.dev/marinellirubens/magic_formula/goto)


Projeto para usar a formula criada por Joel Greenblat no livro "The little book that beats the market" para analisar as acoes da Bovespa, **que fique claro que de forma alguma é uma recomendação de compra ou de venda, apenas um projeto pra auxiliar a analise**.

## Projeto
A ideia desse projeto é usar a formula do Joel Greenblat somado com algumas ideias propostas pelo Ramiro (Clube do Valor) para gerar uma planilha com as informações das ações mais baratas do indice IBRX100, outro proposito desse projeto é servir como um projeto para o meu portifolio como programador

## Requerimentos
Para executar esse programa os seguintes requerimentos devem ser atendidos:
Versão do Python
```shell
$ Python 3.6.5
```
As seguintes libs são utilizadas:
```python
pandas==1.2.4
openpyxl==3.0.7
yahooquery
bs4==0.0.1
requests==2.25.1
numpy==1.20.2
pytest==6.2.4
pytest-cov==2.11.1
```
As libs estão todas listadas no requirements.txt e pode ser instalado usando o pip conforme abaixo:

## Configuração
O programa usa um arquivo de configuração exemplificado no arquivo src/config.example.json
```JSON
{
    "BRX100_URL":"https://statusinvest.com.br/indices/indice-brasil-100",
    "SMALL_URL":"https://statusinvest.com.br/indices/indice-small-cap",
    "IBOV_URL":"https://statusinvest.com.br/indices/ibovespa",
    "IDIV_URL":"https://statusinvest.com.br/indices/indice-dividendos",
    "STATUS_INVEST_URL": "https://statusinvest.com.br/category/advancedsearchresult?search=%7B%22Sector%22%3A%22%22%2C%22SubSector%22%3A%22%22%2C%22Segment%22%3A%22%22%2C%22my_range%22%3A%220%3B25%22%2C%22dy%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22p_L%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22peg_Ratio%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22p_VP%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22p_Ativo%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22margemBruta%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22margemEbit%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22margemLiquida%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22p_Ebit%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22eV_Ebit%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22dividaLiquidaEbit%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22dividaliquidaPatrimonioLiquido%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22p_SR%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22p_CapitalGiro%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22p_AtivoCirculante%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22roe%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22roic%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22roa%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22liquidezCorrente%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22pl_Ativo%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22passivo_Ativo%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22giroAtivos%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22receitas_Cagr5%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22lucros_Cagr5%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22liquidezMediaDiaria%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22vpa%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22lpa%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22valorMercado%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%7D&CategoryType=1",
    "POSTGRESQL_STRING": "postgresql+psycopg2://postgres:example@0.0.0.0/fmsdeinvestimento",
    "MAX_NUMBER_THREADS": 30
}
```
Esse arquivo deve ser usado como base para a criação do arquivo src/config.json
```shell
$ cp src/config.example.json src/config.json 
```

### Diretamente
Devem ser instaladas as dependencias usando os seguintes comandos abaixo: 

Windows:
```bash
# criando o ambiente virtual
$ python -m venv venv
# Iniciando o ambiente virtual
$ .\venv\Scripts\activate.bat
# Instalando as dependencias
$ python -m pip install -r requirements.txt
```

Linux/Macos
```bash
# criando o ambiente virtual
$ python3 -m venv .venv
# Iniciando o ambiente virtual
$ source .venv/bin/activate
# Instalando as dependencias
$ python3 -m pip install -r requirements.txt
```

### Usando o docker
Usando o arquivo docker-compose.yml pode ser criada a imagem com o comando abaixo:
```bash
$ docker-compose build
```


## Executando
Podem ser verificados os comandos de usando o argumento -h:
```shell
usage: stocks_greenblat_magic_formula.py [-h] [-V] [-i INDEX] [-e EBIT]
                                         [-m MARKET_CAP] [-q QTY]

Parses command.

optional arguments:
  -h, --help            show this help message and exit
  -V, --version         Show program version
  -i INDEX, --index INDEX
                        Bovespa index (BRX100, IBOV, SMALL, IDIV)
  -e EBIT, --ebit EBIT  Minimun ebit to be considered
  -m MARKET_CAP, --market_cap MARKET_CAP
                        Minimun market cap
  -q QTY, --qty QTY     Quantity of stocks to be exported.
```

O programa pode ser executado usando o seguinte comando
```bash
$ python3 src/stocks_greenblat_magic_formula.py
```

Ou pode ser executado com o Docker usando o comando abaixo:
```bash
$ docker-compose up -d
```

Esse comando ja esta contido nos arquivos run.sh(Linux e Macos) e run.cmd(Windows), pode ser observado abaixo o output do programa abaixo:
![program_running](program_running.png "program_running")


## Output
Como o objetivo desse programa é listar as ações por ordem de qual esta mais barata, um excel é exportado na pasta xlsx_files com o seguinte padrão de nome:
```
stocks_magic_formula_{yyyymmdd}.xlsx
```
Exemplo de arquivo:

![exemplo_planilha](exemplo_planilha.png "exemplo_planilha")
