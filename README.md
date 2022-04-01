# Magic Formula
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![GitHub Actions](https://img.shields.io/endpoint.svg?url=https%3A%2F%2Factions-badge.atrox.dev%2Fatrox%2Fsync-dotenv%2Fbadge)](https://actions-badge.atrox.dev/marinellirubens/magic_formula/goto)


Projeto para usar a formula criada por Joel Greenblat no livro "The little book that beats the market" para analisar as acoes da Bovespa, **que fique claro que de forma alguma é uma recomendação de compra ou de venda, apenas um projeto pra auxiliar a analise**.

## Projeto
A ideia desse projeto é usar a formula do Joel Greenblat somado com algumas ideias propostas pelo Ramiro (Clube do Valor) para gerar uma planilha com as informações das ações mais baratas do indice IBRX100, outro proposito desse projeto é servir como um projeto para o meu portifolio como programador

```shell
$ magic_formula -V
MagicFormula v1.0.4
```

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
docker-compose build
```

## Instalação via pip
Tambem pode ser instalado via pip com o seguinte comando abaixo:
```shell
python3 -m pip install git+https://github.com/marinellirubens/magic_formula#egg=magic_formula==1.0.4
```

Ou usando o setup.py
```shell
python3 setup.py install
```


## Executando
Podem ser verificados os comandos de usando o argumento -h:
```shell
$ magic_formula -h
usage: magic_formula [-h] [-V] [-t THREADS] [-o OUTPUT_FOLDER] [-i INDEX [INDEX ...]] [-ll LOG_LEVEL] [-e EBIT] [-m MARKET_CAP] [-q QTY] [-d DATABASE] [-l LIST_TICKERS [LIST_TICKERS ...]]

Parses command.

optional arguments:
  -h, --help            show this help message and exit
  -V, --version         Show program version
  -t THREADS, --threads THREADS
                        Max Number of threads
  -o OUTPUT_FOLDER, --output_folder OUTPUT_FOLDER
                        Path for output folder
  -i INDEX [INDEX ...], --index INDEX [INDEX ...]
                        Bovespa indexes (BRX100, IBOV, SMALL, IDIV, MLCX, IGCT, ITAG, IBRA, IGNM, IMAT, ALL) BRX100 -
                        Indice IBRX100 IBOV - IBOVESPA SMALL - Indice de Small Cap IDIV - Indice de Dividendos MLCX -
                        Indice de Mid-Large Cap IGCT - Indice de Governança Corporativa ITAG - Indice de Ações com Tag
                        Along diferenciado IBRA - Indice Brasil Amplo IGNM - Indice de Governança Corporativa - Novo
                        Mercado IMAT - Indice de Materiais Basicos ALL - Todos os Indices anteriores
  -ll LOG_LEVEL, --log_level LOG_LEVEL
                        Log level
  -e EBIT, --ebit EBIT  Minimun ebit to be considered
  -m MARKET_CAP, --market_cap MARKET_CAP
                        Minimun market cap
  -q QTY, --qty QTY     Quantity of stocks to be exported.
  -d DATABASE, --database DATABASE
                        Send information to a database[POSTGRESQL].
  -l LIST_TICKERS [LIST_TICKERS ...], --list_tickers LIST_TICKERS [LIST_TICKERS ...]
                        List stocks instead of using the indexes.
```

O programa pode ser executado usando o seguinte comando
```bash
$ python3 magic_formula/magic_formula_main.py
```
Ou diretamente caso esteja instalado:
```bash
$ magic_formula 
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
stocks_magic_formula_{yyyymmdd}_{INDEXES_NAMES}.xlsx
```
Exemplo de arquivo:

![exemplo_planilha](exemplo_planilha.png "exemplo_planilha")
