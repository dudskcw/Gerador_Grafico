import os
import requests
import pandas as pd
import plotly.express as px
import datetime

NOTION_TOKEN = os.environ.get("NOTION_TOKEN")
DATABASE_ID = os.environ.get("DATABASE_ID")

if not NOTION_TOKEN or not DATABASE_ID:
    raise ValueError("NOTION_TOKEN ou DATABASE_ID não configurados.")

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}


def get_value(props, nome):
    for key in props:
        key_norm = key.lower().replace("í", "i").replace("é", "e")
        nome_norm = nome.lower().replace("í", "i").replace("é", "e")

        if key_norm == nome_norm:
            try:
                prop = props[key]

                if prop["type"] == "select":
                    return prop["select"]["name"] if prop["select"] else "Não definido"

                elif prop["type"] == "multi_select":
                    return ", ".join([x["name"] for x in prop["multi_select"]]) or "Não definido"

                elif prop["type"] == "title":
                    return prop["title"][0]["plain_text"] if prop["title"] else "Sem título"

                elif prop["type"] == "rich_text":
                    return prop["rich_text"][0]["plain_text"] if prop["rich_text"] else "Não definido"

            except:
                return "Não definido"

    return "Não definido"


def carregar_dados_notion():
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"

    all_results = []
    has_more = True
    next_cursor = None

    while has_more:
        payload = {}
        if next_cursor:
            payload["start_cursor"] = next_cursor

        response = requests.post(url, headers=headers, json=payload)

        if response.status_code != 200:
            return None, f"Erro API: {response.status_code}"

        data = response.json()
        all_results.extend(data.get("results", []))

        has_more = data.get("has_more", False)
        next_cursor = data.get("next_cursor")

    if not all_results:
        return None, "Base vazia"

    jogos = []
    consoles = []

    for item in all_results:
        if item.get("archived", False):
            continue

        props = item.get("properties", {})

        jogos.append({
            "Franquia": get_value(props, "Franquia"),
            "Pais": get_value(props, "Países"),
            "NEI": get_value(props, "NEI")
        })

        try:
            for c in props["Console"]["multi_select"]:
                consoles.append(c["name"])
        except:
            pass

    return pd.DataFrame(jogos), pd.DataFrame(consoles, columns=["Console"])


def criar_grafico(df, coluna, titulo):
    df_count = df[coluna].value_counts().reset_index()
    df_count.columns = [coluna, "count"]

    fig = px.pie(df_count, names=coluna, values="count", hole=0.4, title=titulo)

    fig.update_traces(textposition='inside', textinfo='percent+label')

    fig.update_layout(
        autosize=True,
        height=400,
        paper_bgcolor="#1c1c1c",
        font_color="white",
        margin=dict(t=40, b=10, l=10, r=10)
    )

    return fig


def criar_grafico_console(df):
    df_count = df.value_counts().reset_index(name="count")

    fig = px.pie(df_count, names="Console", values="count", hole=0.4, title="Consoles")

    fig.update_traces(textposition='inside', textinfo='percent+label')

    fig.update_layout(
        autosize=True,
        height=400,
        paper_bgcolor="#1c1c1c",
        font_color="white",
        margin=dict(t=40, b=10, l=10, r=10)
    )

    return fig


def gerar_pagina(fig, arquivo, titulo):
    agora = datetime.datetime.now().strftime("%d/%m/%Y às %H:%M")

    with open(arquivo, "w", encoding="utf-8") as f:
        f.write(f"""
        <html>
        <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
        body {{
            background: #1c1c1c;
            color: white;
            font-family: sans-serif;
            margin: 0;
            padding: 20px;
        }}

        .nav a {{
            margin-right: 15px;
            color: #aaa;
            text-decoration: none;
        }}

        .card {{
            background: #252525;
            border-radius: 15px;
            padding: 10px;
            margin-top: 20px;
        }}
        </style>
        </head>

        <body>

        <div class="nav">
            <a href="index.html">Home</a>
            <a href="franquias.html">Franquias</a>
            <a href="paises.html">Países</a>
            <a href="consoles.html">Consoles</a>
            <a href="nei.html">NEI</a>
        </div>

        <div class="card">
        {fig.to_html(full_html=False, include_plotlyjs='cdn')}
        </div>

        <p style="text-align:center; color:#aaa;">
        Atualizado em {agora}
        </p>

        </body>
        </html>
        """)


def gerar_index():
    with open("index.html", "w", encoding="utf-8") as f:
        f.write("""
        <html>
        <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">

        <style>
        body {
            background: #1c1c1c;
            font-family: sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }

        .grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }

        .btn {
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            width: 140px;
            height: 140px;
            border-radius: 20px;
            border: 3px solid transparent;
            background: linear-gradient(135deg, #444, #777) border-box;
            color: white;
            text-decoration: none;
            transition: 0.2s;
        }

        .btn span {
            font-size: 14px;
            margin-top: 8px;
            color: #ccc;
        }

        .btn i {
            font-size: 32px;
        }

        .btn:hover {
            transform: scale(1.08);
            filter: brightness(1.2);
        }

        </style>
        </head>

        <body>

        <div class="grid">
            <a href="franquias.html" class="btn">
                <i>🎮</i>
                <span>Franquias</span>
            </a>

            <a href="paises.html" class="btn">
                <i>🌍</i>
                <span>Países</span>
            </a>

            <a href="consoles.html" class="btn">
                <i>🕹️</i>
                <span>Consoles</span>
            </a>

            <a href="nei.html" class="btn">
                <i>📊</i>
                <span>Experiência</span>
            </a>
        </div>

        </body>
        </html>
        """)

# EXECUÇÃO
df_jogos, df_consoles = carregar_dados_notion()

if df_jogos is not None:
    fig1 = criar_grafico(df_jogos, "Franquia", "Franquias")
    fig2 = criar_grafico(df_jogos, "Pais", "Países")
    fig3 = criar_grafico_console(df_consoles)
    fig4 = criar_grafico(df_jogos, "NEI", "Experiência (NEI)")

    gerar_pagina(fig1, "franquias.html", "Franquias")
    gerar_pagina(fig2, "paises.html", "Países")
    gerar_pagina(fig3, "consoles.html", "Consoles")
    gerar_pagina(fig4, "nei.html", "NEI")

    gerar_index()
