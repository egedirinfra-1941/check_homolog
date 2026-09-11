#Importações iniciais
import requests
import json
import pandas as pd
import numpy as np
from datetime import date
import gspread
import os
from oauth2client.service_account import ServiceAccountCredentials

# Carga do PLANINFRAweb
cred_google = os.getenv('GSHEET_CRED')
url_sheet = os.getenv('GSHEET_KEY_SHEET')

######### BUSCA DO DATAFRAME DO PLANINFRAWEB #########
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
json_key = json.loads(os.getenv("JSON_KEY"))
creds = ServiceAccountCredentials.from_json_keyfile_dict(json_key, scope)
client = gspread.authorize(creds)

# Abrir a planilha pelo nome
# DADO SENSÍVEL
spreadsheet = client.open_by_key(url_sheet)

# Selecionar a folha de trabalho
worksheet = spreadsheet.worksheet("ACD")

# Puxar os dados do intervalo específico
data = worksheet.get('A2:CM')

# Converter para DataFrame do pandas
lista_pw = pd.DataFrame(data[1:], columns=data[0])  # Primeira linha como cabeçalho

# Remover linhas onde todos os valores são NaN
df = lista_pw.dropna(subset=['ID Planinfra'])

df = df[['ID Planinfra',
         'Status',
         'Cidade',
         'Estado',
         'OM',
         'DESCRIÇÃO',
         'RESPONSÁVEL LICITAÇÃO',
         'DATA DA LICITAÇÃO',
         'DATA ENTREGA PROPOSTAS',
         'TIPO LICITACAO',
         'NUMERO LICITACAO']]

print(df.head())

# Ajustando os tipos de atributos
df['Status'] = df['Status'].astype('category')
df['TIPO LICITACAO'] = df['TIPO LICITACAO'].astype('category')
df['DATA ENTREGA PROPOSTAS'] = pd.to_datetime(df['DATA ENTREGA PROPOSTAS'], format="%d/%m/%Y", errors='coerce')
df['DATA DA LICITAÇÃO'] = pd.to_datetime(df['DATA DA LICITAÇÃO'], format="%d/%m/%Y", errors='coerce')
print(df.info())

# Preparando o DataFrame que será usado na pesquisa
df_search = df[
    (df['Status'] == 'LIA') &
    (df['DATA DA LICITAÇÃO'].isna()) &
    (~df['DATA ENTREGA PROPOSTAS'].isna()) &
    (df['DATA ENTREGA PROPOSTAS'] < pd.Timestamp.today())
]

print(df_search.info())

# Listar os dados que farão a pesquisa
email_html = """
<p>Prezados, bom dia!</p>
<p>Segue relação de itens de possíveis homologações a serem checadas:</p>
<ul>
"""

cidades_codigos = {
    "NATAL": 1164,
    "RIO DE JANEIRO": 3243,
    "ANÁPOLIS": 5339,
    "BRASÍLIA": 5570,
    "SÃO JOSÉ DOS CAMPOS": 3825,
    "SÃO PAULO": 3830,
    "CANOAS": 4686,
    "SANTA MARIA": 4971,
    "MANAUS": 112,
    "SÃO GABRIEL DA CACHOEIRA": 126,
    "BELÉM": 170,
    "BARBACENA": 2305,
    "RECIFE": 1597,
    "IAUARETÊ": 126,
    "ESTIRÃO DO EQUADOR": 80,
    "BOA VISTA": 139,
    "CAMPO GRANDE": 5123,
    "PIRASSUNUNGA": 3707,
    "NOVO PROGRESSO": 231,
    "GUARATINGUETÁ": 3476,
    "PARNAMIRIM": 1111,
    "ALCÂNTARA": 454,
    "PORTO VELHO": 17,
    "SÃO LUÍS": 636,
    "SALVADOR": 2163,
    "COARI": 94,
    "LÁBREA": 109,
    "LAGOA SANTA": 2675,
    "OIAPOQUE": 306,
    "BREVES": 179,
    "SANTOS": 3810,
    "GUARULHOS": 3480,
    "MAXARANGUAPE": 1158,
    "FORTALEZA": 950,
    "GAVIÃO PEIXOTO": 3460,
    "BARCELOS": 82,
    "TABATINGA": 130,
    "MATUPÁ": 5249,
    "EIRUNEPÉ": 96,
    "JUÍNA": 5241,
    "CARAUARI": 91,
    "PARINTINS": 120,
    "SÃO FÉLIX DO ARAGUAIA": 5304,
    "MARECHAL THAUMATURGO": 64,
    "REDENÇÃO": 252,
    "TARAUACÁ": 72,
    "ITAITUBA": 209,
    "PARAGOMINAS": 240,
    "HUMAITÁ": 100,
    "MANICORÉ": 113,
    "BOCA DO ACRE": 87,
    "CONCEIÇÃO DO ARAGUAIA": 190,
    "FONTE BOA": 98,
    "ITACOATIARA": 103,
    "MAUÉS": 136,
    "ORIXIMINÁ": 235,
    "ILHA FERNANDO DE NORONHA": 1526,
    "FLORIANÓPOLIS": 4399,
    "CURITIBA": 4006,
    "CAMPO GRANDE (RS)": 5123,
    "CANOAS (ALT)": 4686,
    "SANTA MARIA (ALT)": 4971,
    "BAO VISTA": 139,
    "CARACARAÍ": 142,
    "JABOATÃO DOS GUARARAPES": 1553,
    "SÃO LUÍS (ALT)": 636,
    "ALTO ALEGRE": 138,
    "AMAJARI": 137,
    "QUERARI": 126,
    "MOURA": 82,
    "GUAJARÁ-MIRIM": 10,
    "GUARATINGUETA": 3476,
    "GUARUJÁ": 3479
}

unidades_codigos = {
    "GAP-GL": 404,
    "BANT": 479,
    "GAP-MN": 2552741,
    "CELOG": 544,
    "GAP-SP": 455,
    "BAAN": 565,
    "BAPV": 426,
    "BABV": 481,
    "EPCAR": 430,
    "GAP-DF": 478,
    "GAP-CO": 2552740,
    "AFA": 398,
    "BASM": 2552743,
    "EEAR": 589,
    "GAP-LS": 448,
    "GAP-RF": 2552742,
    "GAP-AF": 2552738,
    "GAP-BE": 2552739,
    "GAP-SJ": 496
}

modalidades_codigos = {
    "pregão": "5|6",
    "concorrência": "3|4"
}

orgaos = "43849|44045|44041|44035|44030|44026|44032|44031"

flag = False

for index, row in df_search.iterrows():
    unidade_text = row['RESPONSÁVEL LICITAÇÃO']
    unidade = unidades_codigos[unidade_text]

    modalidade_text = row['TIPO LICITACAO'].lower()
    modalidade = modalidades_codigos[modalidade_text]

    cidade_text = row['Cidade']
    cidade = cidades_codigos[cidade_text]

    numero_licitacao = row['NUMERO LICITACAO']

    # API real do PNCP
    api_url = "https://pncp.gov.br/api/search/"

    ### Busca por unidade
    # Parâmetros exatos da requisição
    params = {
        'tipos_documento': 'edital',
        'ordenacao': '-data',
        'pagina': 1,
        'tam_pagina': 500,
        'status': 'encerradas',
        'unidades': unidade,
        'modalidades': modalidade,
        'tipos': 1
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json',
        'Referer': 'https://pncp.gov.br/app/editais'
    }

    try:
        response = requests.get(api_url, params=params, headers=headers)
        response.raise_for_status()

        # Parse do JSON
        dados = response.json()

        # Verifica a estrutura dos dados
        if 'items' in dados:
            editais = dados['items']
        elif 'data' in dados:
            editais = dados['data']
        elif 'resultados' in dados:
            editais = dados['resultados']
        elif isinstance(dados, list):
            editais = dados
        else:
            editais = []

        if editais:
            for item in editais:
                item_url = item['item_url'].replace('/compras', 'https://pncp.gov.br/app/editais')

                if numero_licitacao in item['title']:
                    flag = True

                    linha_html = f'<li>Checar ID {row["ID Planinfra"]} ({row["DESCRIÇÃO"]}) — <a href="{item_url}">Clique aqui para abrir o edital</a></li>'

                    print(
                        f"Checar ID {row['ID Planinfra']} "
                        f"({row['DESCRIÇÃO']}) no link {item_url}."
                    )

                    email_html += linha_html + "\n"

        else:
            # Parâmetros exatos da requisição
            params = {
                'tipos_documento': 'edital',
                'ordenacao': '-data',
                'pagina': 1,
                'tam_pagina': 500,
                'status': 'encerradas',
                'municipios': cidade,
                'modalidades': modalidade,
                'tipos': 1,
                'orgaos': orgaos
            }

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json',
                'Referer': 'https://pncp.gov.br/app/editais'
            }

            response = requests.get(api_url, params=params, headers=headers)
            response.raise_for_status()

            # Parse do JSON
            dados = response.json()

            # Verifica a estrutura dos dados
            if 'items' in dados:
                editais = dados['items']
            elif 'data' in dados:
                editais = dados['data']
            elif 'resultados' in dados:
                editais = dados['resultados']
            elif isinstance(dados, list):
                editais = dados
            else:
                editais = []

            if editais:
                for item in editais:
                    item_url = item['item_url'].replace('/compras', 'https://pncp.gov.br/app/editais')

                    if numero_licitacao in item['title']:
                        flag = True

                        linha_html = f'<li>Checar ID {row["ID Planinfra"]} ({row["DESCRIÇÃO"]}) — <a href="{item_url}">Clique aqui para abrir o edital</a></li>'

                        print(
                            f"Checar ID {row['ID Planinfra']} "
                            f"({row['DESCRIÇÃO']}) no link {item_url}."
                        )

                        email_html += linha_html + "\n"

    except requests.exceptions.RequestException as e:
        print(f"Erro ao acessar a API: {e}")

    except Exception as e:
        print(f"Erro ao processar: {e}")
        import traceback
        traceback.print_exc()

if flag == False:
    linha_html = '<li>Nenhum edital encontrado.</li>'
    print("Nenhum edital encontrado.")
    email_html += linha_html + "\n"

# Finalização do conteúdo que seria enviado por e-mail
email_html += """
</ul>
<p>Respeitosamente,<br>Equipe ECCP</p>
"""

assunto = f"Possíveis homologações ({date.today()})"


# Gera um HTML simulando o e-mail, sem enviar nada
def gerar_email_simulado(conteudo, assunto):
    sender_email = os.getenv('SENDER_EMAIL')

    destinatarios = [
        os.getenv('RECEIVER_EMAIL'),
        os.getenv('RECEIVER_EMAIL2'),
        os.getenv('RECEIVER_EMAIL3'),
        os.getenv('RECEIVER_EMAIL4')
    ]

    destinatarios = [email for email in destinatarios if email]

    print()
    print("========== E-MAIL SIMULADO ==========")
    print(f"De: {sender_email}")
    print(f"Para: {', '.join(destinatarios)}")
    print(f"Assunto: {assunto}")
    print("======================================")
    print()

    pasta_saida = os.path.join(os.getcwd(), "email_simulado")
    os.makedirs(pasta_saida, exist_ok=True)

    arquivo_saida = os.path.join(pasta_saida, "email.html")

    destinatarios_html = "<br>".join(destinatarios)

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>{assunto}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 40px;
            color: #222;
            line-height: 1.5;
        }}

        .aviso {{
            padding: 15px;
            margin-bottom: 25px;
            border: 1px solid #d6a700;
            background-color: #fff8d6;
            font-weight: bold;
        }}

        .cabecalho {{
            margin-bottom: 30px;
        }}

        .campo {{
            margin: 8px 0;
        }}

        .rotulo {{
            font-weight: bold;
        }}

        .conteudo {{
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #ccc;
        }}
    </style>
</head>
<body>

    <div class="aviso">
        SIMULAÇÃO — Este e-mail NÃO foi enviado.
    </div>

    <div class="cabecalho">
        <div class="campo">
            <span class="rotulo">De:</span> {sender_email or ""}
        </div>

        <div class="campo">
            <span class="rotulo">Para:</span><br>
            {destinatarios_html}
        </div>

        <div class="campo">
            <span class="rotulo">Assunto:</span> {assunto}
        </div>
    </div>

    <div class="conteudo">
        {conteudo}
    </div>

</body>
</html>
"""

    with open(arquivo_saida, "w", encoding="utf-8") as arquivo:
        arquivo.write(html)

    print(f"E-mail simulado salvo em: {arquivo_saida}")


gerar_email_simulado(email_html, assunto)
