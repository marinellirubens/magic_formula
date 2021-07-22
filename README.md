# Magic Formula
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

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
Windows:
```shell
$ python -m pip install -r requirements.txt
```
Linux/Macos
```shell
$ python3 -m pip install -r requirements.txt
```

## Executando
O programa pode ser executado usando o seguinte comando
```shell
$ python3 src/stocks_greenblat_magic_formula.py
```
Esse comando ja esta contido nos arquivos run.sh(Linux e Macos) e run.cmd(Windows), pode ser observado abaixo o output do programa abaixo:
![program_running](program_running.png "program_running")

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


## Output
Como o objetivo desse programa é listar as ações por ordem de qual esta mais barata, um excel é exportado com o seguinte padrão de nome:
```
stocks_magic_formula_{yyyymmdd}.xlsx
```
Exemplo de arquivo:

![exemplo_planilha](exemplo_planilha.png "exemplo_planilha")
